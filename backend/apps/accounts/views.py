"""
账户模块 - 视图

提供用户认证、个人资料、收货地址和后台用户管理的 API 接口。

视图组织原则：
- AuthViewSet: 所有认证相关操作（注册/登录/登出/刷新token/密码相关）
- ProfileViewSet: 当前用户的个人资料和消费统计
- AddressViewSet: 收货地址的 CRUD + 搜索 + 设置默认
- AdminUserViewSet: 管理员对用户的增删改查 + 操作日志查看

为什么使用 ViewSet 而非单独的 APIView:
ViewSet 将相关操作组织在一起，配合 DRF Router 自动生成 URL 映射，
减少重复的 URL 配置代码，保持路由一致性。
"""
import urllib.request
import urllib.parse
import json
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Address, OperationLog
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    AddressSerializer, ChangePasswordSerializer, SendCodeSerializer, SendSmsCodeSerializer,
    PhoneRegisterSerializer, PhoneLoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
)
from .services import get_consumption_stats
from apps.core.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    认证视图集：处理所有与用户认证相关的操作。

    不绑定到任何模型（GenericViewSet 而非 ModelViewSet），因为认证操作
    不直接对应模型的 CRUD，而是独立的业务逻辑（注册、登录、发验证码等）。

    所有接口默认 AllowAny（无需登录），个别接口如 logout/change_password
    需要 IsAuthenticated，通过 action 级别的 permission_classes 覆盖。
    """

    # 默认权限：任何人都可以访问（具体权限在 action 层面覆盖）
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        根据当前 action 动态返回对应的序列化器类。

        为什么不用 serializer_class 类属性：
        GenericViewSet 的 action 多样（注册、登录、发码等），
        每个 action 需要的序列化器不同，不能用一个序列化器覆盖所有场景。
        get_serializer_class() 让每个 action 指定自己的序列化器。
        """
        if self.action == 'register':
            return RegisterSerializer
        if self.action == 'login':
            return LoginSerializer
        if self.action == 'change_password':
            return ChangePasswordSerializer
        if self.action == 'send_code':
            return SendCodeSerializer
        if self.action == 'password_reset_request':
            return PasswordResetRequestSerializer
        if self.action == 'password_reset_confirm':
            return PasswordResetConfirmSerializer
        return RegisterSerializer

    @action(methods=['post'], detail=False, url_path='send-code')
    def send_code(self, request):
        """
        发送邮箱注册验证码。

        安全措施：
        - 先检查邮箱是否已注册，已注册则拒绝发送（防止滥用）
        - 验证码存储在 Redis 缓存中，5 分钟过期
        - 验证码为 6 位随机数字

        POST /api/auth/send-code/
        Body: {"email": "user@example.com"}
        """
        from .serializers import SendCodeSerializer
        from .verification import generate_email_code, send_verification_email

        # 验证请求数据
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # 检查邮箱是否已被注册（已注册用户不能再注册）
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return Response({'detail': '该邮箱已注册'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成验证码并通过邮件发送
        code = generate_email_code(email)
        send_verification_email(email, code)
        return Response({'detail': '验证码已发送'})

    @action(methods=['post'], detail=False)
    def register(self, request):
        """
        邮箱注册。

        注册成功后自动登录：直接返回 JWT token（access + refresh），
        用户无需再走一遍登录流程。

        POST /api/auth/register/
        Body: {"email": "...", "username": "...", "password": "...", "password2": "...", "code": "..."}
        Response: {"user": {...}, "access": "...", "refresh": "..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 为新注册用户生成 JWT token，实现注册即登录
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def login(self, request):
        """
        用户登录（支持邮箱和手机号两种方式）。

        登录策略：
        1. 先用 account 字段尝试邮箱登录（Django authenticate 默认用 email 字段）
        2. 如果失败且 account 不含 '@'，尝试用手机号查找用户再认证
        3. 如果用户不存在或密码错误，返回统一的错误信息（不泄露是账号不存在还是密码错误）

        POST /api/auth/login/
        Body: {"account": "user@example.com 或 13800138000", "password": "..."}
        Response: {"user": {...}, "access": "...", "refresh": "..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data['account']
        password = serializer.validated_data['password']

        # 尝试邮箱登录：Django 的 authenticate 会用 USERNAME_FIELD（email）匹配
        user = authenticate(request, username=account, password=password)

        # 如果不是邮箱（不含@），尝试手机号登录
        # 手机号登录的流程：先通过 phone 找到用户，再用其 email 进行认证
        if not user and '@' not in account:
            phone_user = User.objects.filter(phone=account).first()
            if phone_user:
                # 用找到的用户的 email 重新认证（Django authenticate 基于 USERNAME_FIELD）
                user = authenticate(request, username=phone_user.email, password=password)

        # 统一错误提示：不区分账号不存在还是密码错误，防止用户枚举攻击
        if not user:
            return Response({'detail': '账号或密码不正确'}, status=status.HTTP_401_UNAUTHORIZED)

        # 检查账号是否被禁用
        if not user.is_active:
            return Response({'detail': '该账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)

        # 生成 JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        用户登出。

        将 refresh token 加入黑名单，使其无法再用于刷新 access token。
        为什么需要黑名单：JWT 是无状态的，token 签发后服务器无法主动使其失效。
        SimpleJWT 的黑名单机制通过将 refresh token 存入数据库来解决这个问题，
        被黑名单的 refresh token 将无法再获取新的 access token。

        POST /api/auth/logout/
        Body: {"refresh": "..."}
        """
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            # 将 refresh token 加入黑名单，使其永久失效
            token.blacklist()
        except Exception:
            # 即使黑名单失败也不影响用户体验，前端会清除本地存储的 token
            pass
        return Response({'detail': '已退出登录'})

    @action(methods=['post'], detail=False, url_path='token/refresh', permission_classes=[permissions.AllowAny])
    def refresh_token(self, request):
        """
        刷新 JWT access token。

        JWT 的典型使用模式：
        - access token 有效期较短（如 30 分钟），减少泄露风险
        - refresh token 有效期较长（如 7 天），用于无感刷新 access token
        - 用户无需频繁输入密码，又能保持较高的安全性

        POST /api/auth/token/refresh/
        Body: {"refresh": "..."}
        Response: {"access": "...", "refresh": "..."}  // 轮转刷新：旧的 refresh 失效，返回新的
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token 不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),  # 轮转刷新：返回新的 refresh token
        })

    @action(methods=['post'], detail=False, url_path='password/change', permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        修改密码（需登录、需旧密码）。

        安全流程：
        1. 用户需提供旧密码（验证操作者是账户本人）
        2. 新密码通过 Django 密码强度校验
        3. 修改成功后记录操作日志（安全审计）

        POST /api/auth/password/change/
        Body: {"old_password": "...", "new_password": "..."}
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # 使用 set_password() 而非直接赋值，确保密码被正确哈希处理
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        # 记录操作日志：密码修改属于敏感操作，需要留痕
        OperationLog.objects.create(user=request.user, action='修改密码')
        return Response({'detail': '密码修改成功'})

    # ======== 密码重置（忘记密码） ========

    @action(methods=['post'], detail=False, url_path='password/reset')
    def password_reset_request(self, request):
        """
        第一步：请求密码重置验证码。

        用户输入注册邮箱，系统验证邮箱已注册后发送验证码。
        为什么只支持邮箱不支持手机号重置：手机号可能已停用或更换，
        邮箱作为注册时的主标识更稳定可靠。

        POST /api/auth/password/reset/
        Body: {"target": "user@example.com"}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data['target']

        from .verification import generate_email_code, send_verification_email

        # 只允许通过邮箱重置密码（手机号可能换号）
        if '@' not in target:
            return Response({'detail': '请输入注册邮箱'}, status=status.HTTP_400_BAD_REQUEST)

        code = generate_email_code(target)
        send_verification_email(target, code)
        return Response({'detail': '验证码已发送'})

    @action(methods=['post'], detail=False, url_path='password/reset/confirm')
    def password_reset_confirm(self, request):
        """
        第二步：确认密码重置。

        用户输入邮箱、验证码和新密码，验证码通过后重置密码。
        支持通过邮箱或手机号查找用户（容错处理）。

        POST /api/auth/password/reset/confirm/
        Body: {"target": "user@example.com", "code": "123456", "new_password": "..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 查找用户：优先用邮箱，其次用手机号（兼容两种注册方式的用户）
        user = User.objects.filter(email=data['target']).first() or User.objects.filter(phone=data['target']).first()
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 重置密码
        user.set_password(data['new_password'])
        user.save()
        return Response({'detail': '密码重置成功'})


class ProfileViewSet(viewsets.GenericViewSet):
    """
    用户个人资料视图集。

    提供当前登录用户的资料查看/修改和消费统计功能。
    所有接口都需要登录（IsAuthenticated）。
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], detail=False)
    def me(self, request):
        """
        获取或更新当前用户的个人资料。

        为什么用 /me 而不是 /{id}：
        - RESTful 设计原则：/me 始终指向当前登录用户，前端无需知道用户 ID
        - 安全性：用户只能修改自己的资料，无法通过修改 URL 中的 ID 来操作他人账户

        GET /api/profile/me/  — 获取当前用户资料
        PATCH /api/profile/me/ — 部分更新当前用户资料
        Body: {"age": 25, "gender": "男"}
        """
        user = request.user
        if request.method == 'GET':
            # GET 请求：返回用户信息
            return Response(UserSerializer(user).data)

        # PATCH 请求：部分更新（partial=True 允许只传需要修改的字段）
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)

    @action(methods=['get'], detail=False, url_path='statistics')
    def statistics(self, request):
        """
        获取当前用户的消费统计数据。

        支持按时间范围筛选：
        - period: month（本月）/ week（本周）/ year（本年）/ all（全部）
        - start, end: 自定义日期范围（覆盖 period 参数）

        GET /api/profile/statistics/?period=month
        Response: {total_orders: 12, total_spent: 3580.50, avg_order: 298.38, ...}

        用途：前端展示个人消费概览仪表盘。
        """
        period = request.query_params.get('period', 'month')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        stats = get_consumption_stats(request.user, period=period, start_date=start, end_date=end)
        return Response(stats)

    @action(methods=['post'], detail=False, url_path='delete-account')
    def delete_account(self, request):
        """用户自行注销账户，清理所有关联数据后删除用户"""
        from apps.cart.models import Cart, CartItem
        from apps.reviews.models import Review
        from apps.orders.models import OrderItem, Order
        from apps.coupons.models import Coupon

        user = request.user
        CartItem.objects.filter(cart__user=user).delete()
        Cart.objects.filter(user=user).delete()
        Review.objects.filter(user=user).delete()
        OrderItem.objects.filter(order__user=user).delete()
        Order.objects.filter(user=user).delete()
        Coupon.objects.filter(user=user).delete()
        Address.objects.filter(user=user).delete()
        OperationLog.objects.filter(user=user).delete()
        user.delete()
        return Response({'detail': '账户已注销'})


class AddressViewSet(viewsets.ModelViewSet):
    """
    收货地址视图集。

    继承 ModelViewSet，自动提供 list/create/retrieve/update/partial_update/destroy
    六个标准 CRUD 操作。额外提供：
    - search: 通过 Nominatim API 搜索真实地理地址
    - set_default: 设置默认地址

    所有操作都限定在当前用户的地址范围内（get_queryset 过滤），
    用户只能管理自己的地址。
    """

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        只返回当前登录用户的地址。

        这是数据隔离的关键：如果不过滤 user，用户可能通过修改 URL 中的 ID
        来访问或修改他人的地址。在 get_queryset 中过滤确保所有操作
        （list/retrieve/update/destroy）都限定在当前用户的范围内。
        """
        return Address.objects.filter(user=self.request.user)

    @action(methods=['get'], detail=False, url_path='search', permission_classes=[permissions.IsAuthenticated])
    def search_place(self, request):
        """
        地址搜索——代理 Nominatim OpenStreetMap API。

        为什么使用 Nominatim 而非国内地图 API：
        - 免费且无需 API Key（适合小型项目）
        - 全球覆盖（支持国际地址）
        - 限制条件：每个请求间隔至少 1 秒（Nominatim 使用策略）

        前端在地址输入框中输入关键词时调用此接口，返回候选地址列表，
        用户选择后自动填充省份、城市等字段，减少手动输入错误。

        GET /api/addresses/search/?keywords=天河区
        Response: [{"name": "天河区", "district": "广东省-广州市-天河区", "address": "..."}, ...]
        """
        keywords = request.query_params.get('keywords', '')
        if not keywords or len(keywords) < 1:
            return Response([])

        # 构建 Nominatim 搜索 URL
        # accept-language=zh 返回中文地址信息
        # limit=8 限制返回结果数量，加快响应速度
        url = (
            'https://nominatim.openstreetmap.org/search'
            f'?q={urllib.parse.quote(keywords)}&format=json&limit=8&addressdetails=1&accept-language=zh'
        )

        # 必须设置 User-Agent 头，Nominatim 要求标识请求来源
        req = urllib.request.Request(url, headers={'User-Agent': 'ECShop/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                results = []
                for item in data[:8]:
                    addr = item.get('address', {})
                    # 拼接省-市-区三级行政区划
                    district_parts = []
                    if addr.get('state'):
                        district_parts.append(addr['state'])
                    if addr.get('city'):
                        district_parts.append(addr['city'])
                    if addr.get('county'):
                        district_parts.append(addr['county'])
                    results.append({
                        'name': item.get('display_name', '').split(',')[0],  # 地址简短名称
                        'district': '-'.join(district_parts) if district_parts else '',
                        'address': item.get('display_name', ''),  # 完整地址
                    })
                return Response(results)
        except Exception as e:
            # 外部 API 调用失败时返回空列表，不阻塞用户（用户可以手动输入地址）
            return Response([])

    @action(methods=['post'], detail=True)
    def set_default(self, request, pk=None):
        """
        设置默认地址。

        实现互斥逻辑：先取消该用户当前的所有默认地址，
        再将指定地址设为默认，保证一个用户只有一个默认地址。

        POST /api/addresses/{id}/set_default/
        """
        address = self.get_object()
        # 先将该用户的所有默认地址标志清除
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        # 将当前地址设为默认
        address.is_default = True
        address.save(update_fields=['is_default'])  # 只更新 is_default 字段，减少数据库写入量
        return Response(self.get_serializer(address).data)


class AdminUserViewSet(viewsets.GenericViewSet):
    """
    管理员用户管理视图集。

    提供后台管理系统中对用户的管理功能：
    - 用户列表（支持按状态、VIP 筛选）
    - 用户详情查看
    - 修改用户状态（禁用/启用、设置/取消 VIP、设置/取消员工）
    - 查看用户操作日志
    - 筛选优惠券发放目标用户

    所有操作都需要管理员权限（IsAdminUser）。
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()

    def list(self, request):
        """
        获取用户列表（分页）。

        支持筛选：
        - is_active=true/false: 按激活状态筛选
        - is_vip=true/false: 按 VIP 状态筛选

        GET /api/admin/users/?is_active=true&is_vip=true&page=1&page_size=20
        """
        qs = self.queryset

        # 按激活状态筛选
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        # 按 VIP 状态筛选
        is_vip = request.query_params.get('is_vip')
        if is_vip is not None:
            qs = qs.filter(is_vip=is_vip.lower() == 'true')

        # 使用 DRF 标准分页器进行分页
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        获取单个用户的详细信息。

        GET /api/admin/users/{id}/
        """
        user = get_object_or_404(self.queryset, id=pk)
        return Response(UserSerializer(user).data)

    def partial_update(self, request, pk=None):
        """
        管理员修改用户状态。

        出于安全考虑，只允许修改白名单中的字段（is_active, is_staff, is_vip），
        不允许管理员修改用户的邮箱、密码等敏感信息。

        每次修改都会记录操作日志，包含旧值和新值，用于审计追踪。

        PATCH /api/admin/users/{id}/
        Body: {"is_active": false, "is_vip": true}
        """
        user = self.queryset.get(id=pk)

        # 白名单：只允许修改这三个字段，防止管理员越权修改其他字段
        allowed_fields = ['is_active', 'is_staff', 'is_vip']
        changed = []  # 记录变更详情

        for field in allowed_fields:
            if field in request.data:
                old_val = getattr(user, field)
                setattr(user, field, request.data[field])
                # 记录变更："is_vip: False -> True"
                changed.append(f'{field}: {old_val} -> {request.data[field]}')

        # 只更新实际有变更的字段
        user.save(update_fields=[f for f in allowed_fields if f in request.data])

        # 记录操作日志，包含"谁"在"什么时间"做了"什么操作"
        if changed:
            OperationLog.objects.create(user=user, action='管理员修改', detail='; '.join(changed))
        return Response(UserSerializer(user).data)

    def destroy(self, request, pk=None):
        """管理员删除用户账户，清理关联数据后删除用户"""
        from apps.cart.models import Cart, CartItem
        from apps.reviews.models import Review
        from apps.orders.models import OrderItem, Order
        from apps.coupons.models import Coupon

        user = self.queryset.get(id=pk)
        # 按依赖顺序清理关联数据
        CartItem.objects.filter(cart__user=user).delete()
        Cart.objects.filter(user=user).delete()
        Review.objects.filter(user=user).delete()
        OrderItem.objects.filter(order__user=user).delete()
        Order.objects.filter(user=user).delete()
        Coupon.objects.filter(user=user).delete()
        Address.objects.filter(user=user).delete()
        OperationLog.objects.filter(user=user).delete()
        # 最后删除用户
        user.delete()
        return Response({'detail': '用户已删除'}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='logs')
    def user_logs(self, request, pk=None):
        """
        查看指定用户的操作日志（最近 50 条）。

        GET /api/admin/users/{id}/logs/
        Response: [{"action": "修改密码", "detail": "", "created_at": "2024-01-01T12:00:00"}, ...]

        用途：客服或管理员排查用户问题时查看历史操作记录。
        """
        logs = OperationLog.objects.filter(user_id=pk)[:50]
        return Response([{
            'action': l.action,
            'detail': l.detail,
            'created_at': l.created_at.isoformat(),
        } for l in logs])

    @action(methods=['get'], detail=False, url_path='filter-targets')
    def filter_targets(self, request):
        """
        筛选发放优惠券的目标用户。

        支持多条件组合筛选：
        - is_vip: 只选 VIP 用户
        - has_orders: 只选有订单的用户
        - min_spent: 最低消费金额门槛
        - keyword: 邮箱/用户名关键词搜索

        结果最多返回 200 条，超出部分截断（防止一次性加载过多数据导致前端渲染卡顿）。

        GET /api/admin/users/filter-targets/?is_vip=true&min_spent=500&keyword=vip
        Response: [{user1}, {user2}, ...]
        """
        from django.db.models import Sum, Q

        # 基础查询：活跃且非超级管理员
        qs = User.objects.filter(is_active=True).exclude(is_superuser=True)

        # 筛选：只选 VIP 用户
        is_vip = request.query_params.get('is_vip')
        if is_vip and is_vip.lower() == 'true':
            qs = qs.filter(is_vip=True)

        # 筛选：只选有过订单的用户（在订单表中有记录）
        has_orders = request.query_params.get('has_orders')
        if has_orders and has_orders.lower() == 'true':
            from apps.orders.models import Order
            order_user_ids = Order.objects.values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=order_user_ids)

        # 筛选：最低消费金额
        min_spent = request.query_params.get('min_spent')
        if min_spent:
            from apps.orders.models import Order
            # 按用户聚合订单总金额，筛选出总消费 >= min_spent 的用户
            spending = (
                Order.objects.values('user_id')
                .annotate(total_spent=Sum('total_amount'))
                .filter(total_spent__gte=float(min_spent))
                .values_list('user_id', flat=True)
            )
            qs = qs.filter(id__in=spending)

        # 关键词搜索：匹配邮箱或用户名
        keyword = request.query_params.get('keyword')
        if keyword:
            qs = qs.filter(Q(email__icontains=keyword) | Q(username__icontains=keyword))

        # 限制返回数量，避免一次性加载过多数据
        serializer = UserSerializer(qs[:200], many=True)
        return Response(serializer.data)

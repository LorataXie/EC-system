"""
优惠券模块 - 视图 (views)

定义优惠券相关的 API 端点，分为两类视图集:
1. CouponViewSet:       面向普通用户的接口 — 仅提供"我的优惠券"查询
2. CouponAdminViewSet:  面向管理员的接口 — 完整 CRUD + 批量发放

设计原则:
- 普通用户只能看自己的券，不能直接修改券状态 (状态由订单系统在消费时更新)
- 管理员可以创建、编辑、删除任意优惠券，以及向指定用户批量发放
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Coupon
from .serializers import CouponSerializer, CouponCreateSerializer, CouponIssueSerializer
from apps.core.permissions import IsAdminUser  # 自定义管理员权限类


class CouponViewSet(viewsets.GenericViewSet):
    """
    普通用户优惠券接口

    使用 GenericViewSet 而非 ModelViewSet，因为:
    - 普通用户不需要标准的 list/retrieve/create/update/delete 操作
    - 只需要一个自定义的 'my' 端点来查询自己的优惠券

    权限: 必须登录后才能访问 (IsAuthenticated)
    """
    # 全部方法都需要 JWT 认证
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False)
    def my(self, request):
        """
        获取当前登录用户的优惠券列表

        GET /api/v1/coupons/my

        支持按状态筛选: GET /api/v1/coupons/my?status=unused
        为何这样设计: 用户通常需要区分"可用券"和"已用/过期券"，
        通过 status 查询参数提供灵活的筛选能力。

        返回用户所有优惠券 (按创建时间倒序，继承自 BaseModel 的 ordering)
        """
        # 从查询参数中获取可选的 status 过滤条件
        status_param = request.query_params.get('status')

        # 只查询当前登录用户的优惠券，保证数据隔离
        qs = Coupon.objects.filter(user=request.user)

        # 如果传了 status 参数，进一步过滤
        if status_param:
            qs = qs.filter(status=status_param)

        # 序列化并返回，many=True 表示序列化查询集 (列表)
        return Response(CouponSerializer(qs, many=True).data)


class CouponAdminViewSet(viewsets.ModelViewSet):
    """
    管理员优惠券接口 (完整 CRUD)

    继承 ModelViewSet，自动提供:
    - GET    /admin/coupons       — 列表 (list)
    - POST   /admin/coupons       — 创建 (create)
    - GET    /admin/coupons/{id}  — 详情 (retrieve)
    - PUT    /admin/coupons/{id}  — 完整更新 (update)
    - PATCH  /admin/coupons/{id}  — 部分更新 (partial_update)
    - DELETE /admin/coupons/{id}  — 删除 (destroy)

    额外自定义端点:
    - POST   /admin/coupons/issue — 批量发放 (issue)

    权限: JWT 认证 + 管理员角色校验 (IsAdminUser)
    """

    # 使用 select_related('user') 预加载用户信息，避免 N+1 查询问题
    # 当查询优惠券列表时，每条券都需要展示用户邮箱，预加载可减少数据库查询次数
    queryset = Coupon.objects.select_related('user').all()

    # 双重权限校验: 先验证 JWT Token (IsAuthenticated)，再验证是否为管理员 (IsAdminUser)
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        """
        根据当前 action 动态选择序列化器

        为何这样设计: 不同操作需要不同的字段集:
        - create: 需要用户填写券的基本信息 (CouponCreateSerializer)
        - issue:  需要用户填写的批量发放参数 (CouponIssueSerializer)
        - 其他:   使用标准的读取序列化器 (CouponSerializer)
        """
        if self.action == 'create':
            return CouponCreateSerializer
        if self.action == 'issue':
            return CouponIssueSerializer
        return CouponSerializer

    @action(methods=['post'], detail=False, url_path='issue')
    def issue(self, request):
        """
        批量发放优惠券给指定用户

        POST /api/v1/admin/coupons/issue

        请求体示例:
        {
            "user_ids": [1, 2, 3],
            "type": "full_reduction",
            "discount_value": 10.00,
            "min_order_amount": 50.00,
            "start_time": "2025-01-01T00:00:00Z",
            "end_time": "2025-12-31T23:59:59Z",
            "count_per_user": 2
        }

        业务逻辑:
        1. 验证请求参数 (通过 CouponIssueSerializer)
        2. 遍历 user_ids，为每个用户创建 count_per_user 张券
        3. 所有券初始状态为 'unused' (未使用)
        4. 返回所有创建的优惠券 JSON 数组，状态码 201

        为何这样设计: 批量发放是电商运营的常见需求 (如新用户注册送券、活动批量赠券)，
        一次 API 调用完成批量操作，避免前端循环调用的性能问题
        """
        # 第一步: 参数验证
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # raise_exception=True → 验证失败自动返回 400
        data = serializer.validated_data

        # 第二步: 批量创建优惠券
        created = []
        for user_id in data['user_ids']:
            # 为每个用户创建 count_per_user 张相同的券
            for _ in range(data['count_per_user']):
                coupon = Coupon.objects.create(
                    type=data['type'],
                    discount_value=data['discount_value'],
                    min_order_amount=data['min_order_amount'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    status='unused',   # 新发放的券默认状态: 未使用
                    user_id=user_id,    # 绑定到具体用户
                )
                created.append(coupon)

        # 第三步: 序列化并返回创建结果
        return Response(CouponSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

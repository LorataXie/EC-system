import urllib.request
import urllib.parse
import json
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Address
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
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
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
        from .serializers import SendCodeSerializer
        from .verification import generate_code, send_verification_email
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return Response({'detail': '该邮箱已注册'}, status=status.HTTP_400_BAD_REQUEST)

        code = generate_code(email)
        send_verification_email(email, code)
        return Response({'detail': '验证码已发送'})

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data['account']
        password = serializer.validated_data['password']

        # Try email first, then phone
        user = authenticate(request, username=account, password=password)
        if not user and '@' not in account:
            # Phone login — find user by phone, authenticate with username
            phone_user = User.objects.filter(phone=account).first()
            if phone_user:
                user = authenticate(request, username=phone_user.email, password=password)

        if not user:
            return Response({'detail': '账号或密码不正确'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({'detail': '该账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    @action(methods=['post'], detail=False, permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass
        return Response({'detail': '已退出登录'})

    @action(methods=['post'], detail=False, url_path='token/refresh', permission_classes=[permissions.AllowAny])
    def refresh_token(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token 不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
        })

    @action(methods=['post'], detail=False, url_path='password/change', permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': '密码修改成功'})

    # ======== Password reset ========

    @action(methods=['post'], detail=False, url_path='password/reset')
    def password_reset_request(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data['target']

        from .verification import generate_email_code, send_verification_email

        if '@' not in target:
            return Response({'detail': '请输入注册邮箱'}, status=status.HTTP_400_BAD_REQUEST)

        code = generate_email_code(target)
        send_verification_email(target, code)
        return Response({'detail': '验证码已发送'})

    @action(methods=['post'], detail=False, url_path='password/reset/confirm')
    def password_reset_confirm(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.filter(email=data['target']).first() or User.objects.filter(phone=data['target']).first()
        if not user:
            return Response({'detail': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data['new_password'])
        user.save()
        return Response({'detail': '密码重置成功'})


class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], detail=False)
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            return Response(UserSerializer(user).data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)

    @action(methods=['get'], detail=False, url_path='statistics')
    def statistics(self, request):
        period = request.query_params.get('period', 'month')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        stats = get_consumption_stats(request.user, period=period, start_date=start, end_date=end)
        return Response(stats)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    @action(methods=['get'], detail=False, url_path='search', permission_classes=[permissions.IsAuthenticated])
    def search_place(self, request):
        """代理高德地图POI搜索"""
        keywords = request.query_params.get('keywords', '')
        if not keywords:
            return Response([])

        key = 'efb252f9c97e90648513ddff306b5226'
        url = f'https://restapi.amap.com/v3/assistant/inputtips?key={key}&keywords={urllib.parse.quote(keywords)}&datatype=all'
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get('status') == '1':
                    results = []
                    for tip in data.get('tips', []):
                        if tip.get('location'):
                            results.append({
                                'name': tip['name'],
                                'district': tip.get('district', ''),
                                'address': tip.get('address', ''),
                            })
                    return Response(results[:8])
        except Exception:
            pass
        return Response([])

    @action(methods=['post'], detail=True)
    def set_default(self, request, pk=None):
        address = self.get_object()
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save(update_fields=['is_default'])
        return Response(self.get_serializer(address).data)


class AdminUserViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()

    def list(self, request):
        qs = self.queryset
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        is_vip = request.query_params.get('is_vip')
        if is_vip is not None:
            qs = qs.filter(is_vip=is_vip.lower() == 'true')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        user = self.queryset.get(id=pk)
        return Response(UserSerializer(user).data)

    def partial_update(self, request, pk=None):
        user = self.queryset.get(id=pk)
        allowed_fields = ['is_active', 'is_staff', 'is_vip']
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save(update_fields=[f for f in allowed_fields if f in request.data])
        return Response(UserSerializer(user).data)

    @action(methods=['get'], detail=False, url_path='filter-targets')
    def filter_targets(self, request):
        """筛选发放优惠券的目标用户"""
        from django.db.models import Sum, Q

        qs = User.objects.filter(is_active=True).exclude(is_superuser=True)

        # Filter: VIP users
        is_vip = request.query_params.get('is_vip')
        if is_vip and is_vip.lower() == 'true':
            qs = qs.filter(is_vip=True)

        # Filter: users with orders
        has_orders = request.query_params.get('has_orders')
        if has_orders and has_orders.lower() == 'true':
            from apps.orders.models import Order
            order_user_ids = Order.objects.values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=order_user_ids)

        # Filter: min spending amount
        min_spent = request.query_params.get('min_spent')
        if min_spent:
            from apps.orders.models import Order
            spending = (
                Order.objects.values('user_id')
                .annotate(total_spent=Sum('total_amount'))
                .filter(total_spent__gte=float(min_spent))
                .values_list('user_id', flat=True)
            )
            qs = qs.filter(id__in=spending)

        # Keyword search
        keyword = request.query_params.get('keyword')
        if keyword:
            qs = qs.filter(Q(email__icontains=keyword) | Q(username__icontains=keyword))

        serializer = UserSerializer(qs[:200], many=True)
        return Response(serializer.data)

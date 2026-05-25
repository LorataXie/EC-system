from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
from .models import Order
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, CreateOrderSerializer,
)
from .services import create_order
from .permissions import IsOrderOwnerOrAdmin
from apps.cart.models import CartItem
from apps.core.permissions import IsAdminUser


class OrderViewSet(viewsets.GenericViewSet):
    """
    用户端订单视图集

    提供普通用户的订单相关操作接口，所有操作都需要登录。
    核心功能包括：
    - my: 查看我的订单列表（支持按状态筛选和分页）
    - place_order: 提交下单（从购物车选中商品创建订单）
    - order_detail: 查看订单详情
    - pay: 模拟支付（自动发货，生成物流单号）
    - cancel: 取消待支付订单（恢复商品库存）
    - confirm_delivery: 确认收货（shipped -> completed）
    - request_refund: 申请退款
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False)
    def my(self, request):
        """
        获取当前用户的订单列表。

        始终按当前登录用户过滤——即使是管理员，这里也只显示其个人订单。
        支持通过 status 查询参数筛选特定状态的订单。
        预加载优惠券和商品明细以减少数据库查询次数。
        支持分页，返回 paginated response。
        """
        # Always filter by the requesting user — even admin only sees their own personal orders here
        queryset = Order.objects.filter(user=request.user).select_related('coupon').prefetch_related('items__product').order_by('-created_at')
        # 支持按订单状态筛选
        st = request.query_params.get('status')
        if st:
            queryset = queryset.filter(status=st)
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='place')
    def place_order(self, request):
        """
        提交下单：从购物车选中商品创建订单。

        处理流程：
        1. 验证请求数据（地址 ID、商品条目 ID、优惠券 ID）
        2. 从数据库获取选中的购物车条目（确保属于当前用户）
        3. 校验收货地址是否存在且属于当前用户
        4. 校验优惠券是否存在
        5. 调用 services.create_order 原子性地创建订单
           （事务内完成：创建订单 -> 扣减库存 -> 更新销量 -> 删除购物车条目）
        6. 返回创建成功的订单详情

        关键保护：
        - 只处理属于当前用户的购物车条目
        - 地址必须属于当前用户
        - 使用数据库事务确保数据一致性
        """
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 获取用户选中的购物车条目，确保属于当前用户
        selected_items = CartItem.objects.filter(
            id__in=data['item_ids'],
            cart__user=request.user
        ).select_related('product')

        if not selected_items:
            return Response({'detail': '没有找到选中的商品'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate address exists and belongs to user
        # 校验收货地址是否存在且属于当前用户
        address_id = data.get('address_id')
        if address_id:
            from apps.accounts.models import Address
            get_object_or_404(Address, id=address_id, user=request.user)

        # 校验优惠券是否存在
        coupon = None
        if data.get('coupon_id'):
            from apps.coupons.models import Coupon
            coupon = get_object_or_404(Coupon, id=data['coupon_id'])

        # 调用服务层创建订单（事务保护）
        try:
            order = create_order(
                user=request.user,
                selected_items=selected_items,
                address_id=address_id,
                coupon=coupon,
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=True, url_path='detail')
    def order_detail(self, request, pk=None):
        """
        查看订单详情。

        根据订单主键获取订单完整信息，并校验该订单属于当前用户。
        管理员也可通过此接口查看订单详情（IsOrderOwnerOrAdmin 权限）。
        """
        order = get_object_or_404(Order, pk=pk, user=request.user)
        self.check_object_permissions(request, order)
        return Response(OrderDetailSerializer(order).data)

    @action(methods=['post'], detail=True, url_path='pay')
    def pay(self, request, pk=None):
        """
        模拟支付订单。

        将订单状态从 pending 变更为 shipped（已发货），
        并自动生成物流单号（格式：SF + 时间戳 + 4位随机数）和配送方式。

        简化设计：
        - 实际项目中支付和发货是两个独立步骤
        - 此处为了演示简化为"支付即发货"，跳过 paid 中间状态
        - 物流单号自动生成，模拟第三方物流对接
        """
        order = get_object_or_404(Order, pk=pk, user=request.user, status='pending')
        order.status = 'shipped'
        # 生成模拟物流单号：顺丰前缀 + 时间戳 + 随机数
        ts = timezone.now().strftime('%Y%m%d%H%M%S')
        order.tracking_number = f'SF{ts}{random.randint(1000,9999)}'
        order.shipping_method = '顺丰快递'
        order.save(update_fields=['status', 'tracking_number', 'shipping_method'])
        return Response({'detail': '支付成功，已自动发货'})

    @action(methods=['post'], detail=True, url_path='cancel')
    def cancel(self, request, pk=None):
        """
        取消待支付订单。

        仅 pending 状态的订单可取消。
        取消时恢复所有订单明细中商品的库存，
        以确保不会因取消订单而造成库存被永久锁定。
        """
        order = get_object_or_404(Order, pk=pk, user=request.user, status='pending')
        # Restore stock
        # 恢复订单中所有商品的库存
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        return Response({'detail': '订单已取消'})

    @action(methods=['post'], detail=True, url_path='confirm-delivery')
    def confirm_delivery(self, request, pk=None):
        """
        确认收货。

        将订单状态从 shipped 变更为 completed（已完成）。
        仅 shipped 状态的订单可以确认收货。

        实际项目中此处可能涉及：
        - 自动结算到商家账户
        - 触发评价提醒
        - 更新用户积分等
        """
        order = get_object_or_404(Order, pk=pk, user=request.user, status='shipped')
        order.status = 'completed'
        order.save(update_fields=['status'])
        return Response({'detail': '已确认收货'})

    @action(methods=['post'], detail=True, url_path='refund')
    def request_refund(self, request, pk=None):
        """
        申请退款。

        仅 paid 或 shipped 状态的订单可以申请退款。
        申请后订单的 refund_status 变为 requested（申请中），
        需要管理员在后台审核（同意或拒绝）。
        """
        order = get_object_or_404(Order, pk=pk, user=request.user, status__in=['paid', 'shipped'])
        order.refund_status = 'requested'
        order.save(update_fields=['refund_status'])
        return Response({'detail': '退款申请已提交'})


class OrderAdminViewSet(viewsets.GenericViewSet):
    """
    管理员订单视图集

    提供管理员的后台订单管理功能。所有操作需要管理员权限。
    核心功能包括：
    - list_all: 查看所有订单（支持多种筛选条件和分页）
    - order_detail: 查看任意订单详情（不受用户限制）
    - ship: 发货（录入物流单号和配送方式）
    - cancel_expired: 批量取消超时未支付订单
    - process_refund: 处理退款申请（同意或拒绝）
    - complete_order: 手动标记订单为已完成
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    # 预加载用户、优惠券和商品明细，优化查询效率
    queryset = Order.objects.all().select_related('user', 'coupon').prefetch_related('items__product')

    @action(methods=['get'], detail=False, url_path='all')
    def list_all(self, request):
        """
        获取所有订单列表（管理员视角）。

        支持多维度筛选：
        - status: 按订单状态筛选
        - user_id: 按用户 ID 筛选
        - date_from / date_to: 按创建时间范围筛选

        支持分页返回。
        """
        qs = self.queryset
        # 按订单状态筛选
        st = request.query_params.get('status')
        if st: qs = qs.filter(status=st)
        # 按用户筛选
        user_id = request.query_params.get('user_id')
        if user_id: qs = qs.filter(user_id=user_id)
        # 按创建时间起始日期筛选
        date_from = request.query_params.get('date_from')
        if date_from: qs = qs.filter(created_at__gte=date_from)
        # 按创建时间截止日期筛选
        date_to = request.query_params.get('date_to')
        if date_to: qs = qs.filter(created_at__lte=date_to)
        # 分页处理
        page = self.paginate_queryset(qs)
        serializer = OrderListSerializer(page, many=True) if page else OrderListSerializer(qs, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='detail')
    def order_detail(self, request, pk=None):
        """
        查看任意订单的详情（管理员视角）。

        与用户端 order_detail 不同，此处不限制订单所属用户，
        管理员可以查看系统中任何订单的完整信息。
        """
        order = get_object_or_404(self.queryset, pk=pk)
        return Response(OrderDetailSerializer(order).data)

    @action(methods=['post'], detail=True, url_path='ship')
    def ship(self, request, pk=None):
        """
        管理员发货操作。

        将订单状态从 paid 变更为 shipped（已发货），
        同时录入物流单号和配送方式（由请求数据提供）。
        实际项目中此处可能对接第三方物流 API 生成真实运单。
        """
        order = get_object_or_404(self.queryset, pk=pk, status='paid')
        order.status = 'shipped'
        order.tracking_number = request.data.get('tracking_number', '')
        order.shipping_method = request.data.get('shipping_method', '')
        order.save(update_fields=['status', 'tracking_number', 'shipping_method'])
        return Response({'detail': '已发货'})

    @action(methods=['post'], detail=False, url_path='cancel-expired')
    def cancel_expired(self, request):
        """
        批量取消超时未支付的订单。

        管理员可以指定超时分钟数（默认30分钟），
        系统会自动取消所有超过该时间仍处于 pending 状态的订单，
        同时恢复对应商品的库存。
        适用于清理僵尸订单、释放被锁定的库存。
        """
        minutes = int(request.data.get('minutes', 30))
        from .services import cancel_expired_orders
        count = cancel_expired_orders(minutes)
        return Response({'detail': f'已取消 {count} 笔超时订单'})

    @action(methods=['post'], detail=True, url_path='process-refund')
    def process_refund(self, request, pk=None):
        """
        处理退款申请。

        管理员审核退款申请，支持两种操作：
        - approve（同意退款）：退款状态变为 refunded，订单状态变为 cancelled，
          同时恢复所有商品库存
        - reject（拒绝退款）：退款状态变为 rejected，订单维持原状态

        只有 refund_status 为 requested（申请中）的订单可以被处理。
        """
        order = get_object_or_404(self.queryset, pk=pk, refund_status='requested')
        action = request.data.get('action')
        if action == 'approve':
            # 同意退款：退款状态设为已退款，订单取消，恢复库存
            order.refund_status = 'refunded'
            order.status = 'cancelled'
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        elif action == 'reject':
            # 拒绝退款：仅更新退款状态为已拒绝
            order.refund_status = 'rejected'
        order.save(update_fields=['refund_status', 'status'])
        return Response({'detail': '已处理'})

    @action(methods=['post'], detail=True, url_path='complete')
    def complete_order(self, request, pk=None):
        """
        手动将订单标记为已完成。

        将 delivered（已送达）状态的订单变更为 completed（已完成）。
        通常情况下订单由用户确认收货自动完成，此接口为管理员提供
        手动操作的途径，用于处理异常情况。
        """
        order = get_object_or_404(self.queryset, pk=pk, status='delivered')
        order.status = 'completed'
        order.save(update_fields=['status'])
        return Response({'detail': '已标记为完成'})
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Order.objects.all().select_related('user', 'coupon').prefetch_related('items__product')

    @action(methods=['get'], detail=False, url_path='all')
    def list_all(self, request):
        qs = self.queryset
        user_id = request.query_params.get('user_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if user_id:
            qs = qs.filter(user_id=user_id)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(OrderListSerializer(qs, many=True).data)

    @action(methods=['get'], detail=True, url_path='detail')
    def order_detail(self, request, pk=None):
        order = get_object_or_404(self.queryset, pk=pk)
        return Response(OrderDetailSerializer(order).data)


# ======== Analytics Views ========
# 数据分析相关视图：为后台管理仪表盘提供 KPI、销售趋势、热销商品等数据

from rest_framework.decorators import api_view, permission_classes
from .analytics import get_dashboard_kpis, get_sales_trend, get_recent_orders, get_hot_products


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def dashboard_view(request):
    """
    仪表盘 KPI 视图

    返回后台管理首页的核心指标数据，包括：
    - 总营收（所有订单总金额之和）
    - 订单总数
    - 用户总数
    - 商品总数

    仅管理员可访问。
    """
    return Response(get_dashboard_kpis())


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def sales_trend_view(request):
    """
    销售趋势视图

    返回最近 N 个月的销售趋势数据，按月份分组统计：
    - 每月销售总额
    - 每月订单数量

    默认返回最近 6 个月，可通过 ?months= 参数调整。
    用于后台仪表盘绘制销售趋势折线图。
    """
    months = int(request.query_params.get('months', 6))
    return Response(get_sales_trend(months))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def hot_products_view(request):
    """
    热销商品视图

    返回销量最高的 Top N 商品列表，按商品在所有订单中
    出现的总购买数量降序排列。

    默认返回前 10 名，可通过 ?limit= 参数调整。
    用于后台仪表盘展示热销商品排行榜。
    """
    limit = int(request.query_params.get('limit', 10))
    return Response(get_hot_products(limit))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def recent_orders_view(request):
    """
    最近订单视图

    返回最近的 N 笔订单列表，按创建时间倒序排列。

    默认返回 10 笔，可通过 ?limit= 参数调整。
    用于后台仪表盘快速查看最新订单动态。
    """
    limit = int(request.query_params.get('limit', 10))
    return Response(get_recent_orders(limit))

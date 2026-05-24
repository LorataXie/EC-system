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
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False)
    def my(self, request):
        # Always filter by the requesting user — even admin only sees their own personal orders here
        queryset = Order.objects.filter(user=request.user).select_related('coupon').prefetch_related('items__product').order_by('-created_at')
        st = request.query_params.get('status')
        if st:
            queryset = queryset.filter(status=st)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='place')
    def place_order(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        selected_items = CartItem.objects.filter(
            id__in=data['item_ids'],
            cart__user=request.user
        ).select_related('product')

        if not selected_items:
            return Response({'detail': '没有找到选中的商品'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate address exists and belongs to user
        address_id = data.get('address_id')
        if address_id:
            from apps.accounts.models import Address
            get_object_or_404(Address, id=address_id, user=request.user)

        coupon = None
        if data.get('coupon_id'):
            from apps.coupons.models import Coupon
            coupon = get_object_or_404(Coupon, id=data['coupon_id'])

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
        order = get_object_or_404(Order, pk=pk, user=request.user)
        self.check_object_permissions(request, order)
        return Response(OrderDetailSerializer(order).data)

    @action(methods=['post'], detail=True, url_path='pay')
    def pay(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user, status='pending')
        order.status = 'shipped'
        ts = timezone.now().strftime('%Y%m%d%H%M%S')
        order.tracking_number = f'SF{ts}{random.randint(1000,9999)}'
        order.shipping_method = '顺丰快递'
        order.save(update_fields=['status', 'tracking_number', 'shipping_method'])
        return Response({'detail': '支付成功，已自动发货'})

    @action(methods=['post'], detail=True, url_path='cancel')
    def cancel(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user, status='pending')
        # Restore stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        return Response({'detail': '订单已取消'})

    @action(methods=['post'], detail=True, url_path='confirm-delivery')
    def confirm_delivery(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user, status='shipped')
        order.status = 'completed'
        order.save(update_fields=['status'])
        return Response({'detail': '已确认收货'})


class OrderAdminViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Order.objects.all().select_related('user', 'coupon').prefetch_related('items__product')

    @action(methods=['get'], detail=False, url_path='all')
    def list_all(self, request):
        qs = self.queryset
        st = request.query_params.get('status')
        if st: qs = qs.filter(status=st)
        user_id = request.query_params.get('user_id')
        if user_id: qs = qs.filter(user_id=user_id)
        date_from = request.query_params.get('date_from')
        if date_from: qs = qs.filter(created_at__gte=date_from)
        date_to = request.query_params.get('date_to')
        if date_to: qs = qs.filter(created_at__lte=date_to)
        page = self.paginate_queryset(qs)
        serializer = OrderListSerializer(page, many=True) if page else OrderListSerializer(qs, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='detail')
    def order_detail(self, request, pk=None):
        order = get_object_or_404(self.queryset, pk=pk)
        return Response(OrderDetailSerializer(order).data)

    @action(methods=['post'], detail=True, url_path='ship')
    def ship(self, request, pk=None):
        order = get_object_or_404(self.queryset, pk=pk, status='paid')
        order.status = 'shipped'
        order.tracking_number = request.data.get('tracking_number', '')
        order.shipping_method = request.data.get('shipping_method', '')
        order.save(update_fields=['status', 'tracking_number', 'shipping_method'])
        return Response({'detail': '已发货'})

    @action(methods=['post'], detail=False, url_path='cancel-expired')
    def cancel_expired(self, request):
        minutes = int(request.data.get('minutes', 30))
        from .services import cancel_expired_orders
        count = cancel_expired_orders(minutes)
        return Response({'detail': f'已取消 {count} 笔超时订单'})
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

from rest_framework.decorators import api_view, permission_classes
from .analytics import get_dashboard_kpis, get_sales_trend, get_recent_orders, get_hot_products


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def dashboard_view(request):
    return Response(get_dashboard_kpis())


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def sales_trend_view(request):
    months = int(request.query_params.get('months', 6))
    return Response(get_sales_trend(months))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def hot_products_view(request):
    limit = int(request.query_params.get('limit', 10))
    return Response(get_hot_products(limit))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsAdminUser])
def recent_orders_view(request):
    limit = int(request.query_params.get('limit', 10))
    return Response(get_recent_orders(limit))

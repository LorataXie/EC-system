from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from apps.core.permissions import IsOwnerOrAdmin, IsAdminUser


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product')
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        from apps.orders.models import Order
        order_id = self.request.data.get('order')
        user = self.request.user
        order = Order.objects.filter(id=order_id, user=user).first()
        if not order:
            raise serializers.ValidationError({'order': '订单不存在'})
        if order.status != 'completed':
            raise serializers.ValidationError({'order': '只能评价已完成的订单'})
        serializer.save()

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        order_id = self.request.query_params.get('order_id')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs


class ReviewAdminViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Review.objects.all()

    @action(methods=['get'], detail=False)
    def all(self, request):
        qs = self.queryset.select_related('user', 'product')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ReviewSerializer(page, many=True).data)
        return Response(ReviewSerializer(qs, many=True).data)

    @action(methods=['delete'], detail=True)
    def remove(self, request, pk=None):
        self.queryset.get(id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

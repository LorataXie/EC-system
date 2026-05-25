from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']

    def get_product_name(self, obj):
        return obj.product.name

    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'refund_status', 'total_amount', 'discount_amount', 'coupon', 'address_snapshot', 'tracking_number', 'shipping_method', 'items', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'discount_amount', 'coupon', 'address_snapshot', 'tracking_number', 'shipping_method', 'items', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.UUIDField()
    item_ids = serializers.ListField(child=serializers.UUIDField())
    coupon_id = serializers.UUIDField(required=False, allow_null=True)

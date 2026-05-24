from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_stock = serializers.IntegerField(source='product.stock', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'product_name',
                  'product_price', 'product_stock', 'quantity', 'subtotal', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_subtotal(self, obj):
        return obj.quantity * obj.product.price


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class BatchDeleteSerializer(serializers.Serializer):
    item_ids = serializers.ListField(child=serializers.UUIDField())


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'item_count']

    def get_total_amount(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())

    def get_item_count(self, obj):
        return obj.items.count()

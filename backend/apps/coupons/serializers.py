from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Coupon
        fields = ['id', 'type', 'discount_value', 'min_order_amount',
                  'start_time', 'end_time', 'status', 'user', 'user_email', 'created_at']
        read_only_fields = ['id', 'created_at']


class CouponCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'type', 'discount_value', 'min_order_amount',
                  'start_time', 'end_time', 'status', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CouponIssueSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())
    type = serializers.ChoiceField(choices=Coupon.COUPON_TYPES)
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    count_per_user = serializers.IntegerField(default=1, min_value=1)

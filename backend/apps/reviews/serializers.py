from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_name', 'user', 'user_name',
                  'order', 'rating', 'comment', 'image', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'order', 'rating', 'comment', 'image']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

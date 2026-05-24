from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        children = obj.get_children()
        if children.exists():
            return CategorySerializer(children, many=True).data
        return []


class CategoryFlatSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_name']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'price', 'stock', 'sales_count', 'rating_avg', 'category', 'category_name', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'description', 'price', 'stock',
                  'category', 'category_name', 'created_at', 'updated_at']


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

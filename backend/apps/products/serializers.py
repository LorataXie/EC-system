from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    树形分类序列化器

    递归序列化分类的树形结构——每个分类包含其子分类列表。
    用于前端展示多级分类导航菜单，通过 children 字段递归嵌套。
    """
    # 动态获取子分类列表，使用 SerializerMethodField 实现递归序列化
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        """
        递归获取当前分类的所有子分类。

        通过 MPTT 的 get_children() 方法获取直接子节点，
        如果存在子节点则递归使用 CategorySerializer 序列化，
        否则返回空列表终止递归。
        """
        children = obj.get_children()
        if children.exists():
            return CategorySerializer(children, many=True).data
        return []


class CategoryFlatSerializer(serializers.ModelSerializer):
    """
    扁平分类序列化器

    将所有分类以扁平列表形式返回，每个分类附带父分类名称，
    方便后台管理页面使用下拉选择或表格展示。
    不包含树形嵌套结构。
    """
    # 通过外键 parent.name 获取父分类名称，避免额外查询
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_name']


class ProductListSerializer(serializers.ModelSerializer):
    """
    商品列表序列化器

    用于商品列表页展示，包含核心字段（名称、图片、价格、销量、评分等），
    不包含 description 详细描述以减少数据传输量、提高列表加载速度。
    category_name 通过外键直接获取，避免 N+1 查询。
    """
    # 通过外键直接获取分类名称，使用 select_related 优化查询
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'price', 'stock', 'sales_count', 'rating_avg', 'category', 'category_name', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    商品详情序列化器

    用于商品详情页展示，在列表字段基础上增加 description 描述、
    updated_at 更新时间等完整信息，方便用户全面了解商品。
    """
    # 通过外键直接获取分类名称
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'description', 'price', 'stock',
                  'category', 'category_name', 'created_at', 'updated_at']


class ProductAdminSerializer(serializers.ModelSerializer):
    """
    管理员商品序列化器

    用于后台管理，暴露所有字段（包括敏感字段如 sales_count 等），
    允许管理员对商品进行完整的增删改查操作。
    created_at 和 updated_at 设为只读，由系统自动维护。
    """
    class Meta:
        model = Product
        fields = '__all__'
        # 创建时间和更新时间由系统自动维护，不允许手动修改
        read_only_fields = ['created_at', 'updated_at']

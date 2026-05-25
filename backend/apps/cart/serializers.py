from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    购物车条目序列化器

    序列化单个购物车条目，除了自身信息外，还会从关联的 Product
    中提取商品名称、价格、库存等信息展示给用户。
    subtotal（小计）通过计算字段动态生成。
    """
    # 商品 ID（只读，来自关联的 Product）
    product_id = serializers.UUIDField(source='product.id', read_only=True)
    # 商品名称（只读，来自关联的 Product）
    product_name = serializers.CharField(source='product.name', read_only=True)
    # 商品单价（只读，来自关联的 Product）
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    # 商品库存（只读，来自关联的 Product），前端用于限制购买数量
    product_stock = serializers.IntegerField(source='product.stock', read_only=True)
    # 小计 = 数量 x 单价，动态计算
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'product_name',
                  'product_price', 'product_stock', 'quantity', 'subtotal', 'created_at']
        # id 和创建时间由系统自动维护
        read_only_fields = ['id', 'created_at']

    def get_subtotal(self, obj):
        """
        计算当前购物车条目的小计金额。

        小计 = 商品数量 x 商品单价。
        每次序列化时动态计算，不需要存储到数据库中，
        因为价格可能变化，实时计算更准确。
        """
        return obj.quantity * obj.product.price


class AddCartItemSerializer(serializers.Serializer):
    """
    添加购物车请求序列化器

    用于 POST /cart/items/ 接口，验证前端提交的添加商品请求数据。
    不是 ModelSerializer，因为不需要直接操作数据库——添加逻辑在视图中处理。
    """
    # 要添加的商品 ID
    product_id = serializers.UUIDField()
    # 添加数量，默认为1，最小为1
    quantity = serializers.IntegerField(default=1, min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """
    更新购物车条目请求序列化器

    用于 PATCH /cart/items/{id}/ 接口，修改购物车中某商品的数量。
    只接收数量字段，最小为1（数量为0应该用删除接口）。
    """
    # 新的商品数量，最小为1
    quantity = serializers.IntegerField(min_value=1)


class BatchDeleteSerializer(serializers.Serializer):
    """
    批量删除购物车条目请求序列化器

    用于 POST /cart/items/batch-delete/ 接口，
    支持一次性删除多个购物车条目，避免前端逐个调用删除接口。
    """
    # 要删除的购物车条目 ID 列表
    item_ids = serializers.ListField(child=serializers.UUIDField())


class CartSerializer(serializers.ModelSerializer):
    """
    购物车序列化器

    序列化整个购物车，包含所有商品条目（items）、
    总金额（total_amount）和商品种类数（item_count）。
    用于前端购物车页面展示完整购物车信息。
    """
    # 嵌套序列化所有购物车条目
    items = CartItemSerializer(many=True, read_only=True)
    # 购物车总金额：所有条目小计之和
    total_amount = serializers.SerializerMethodField()
    # 购物车商品种类数（不同商品的数量，不是总件数）
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'item_count']

    def get_total_amount(self, obj):
        """
        计算购物车所有商品的总金额。

        遍历所有购物车条目，累加每个条目的 数量 x 单价。
        使用 Python 计算而不是数据库聚合，因为 items 已经加载到内存。
        """
        return sum(item.quantity * item.product.price for item in obj.items.all())

    def get_item_count(self, obj):
        """
        获取购物车中不同商品的种类数。

        注意：这是商品种类数而非总件数。
        例如购物车有 3 个 iPhone + 2 个 MacBook，item_count = 2。
        """
        return obj.items.count()

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    订单明细序列化器

    序列化订单中的单个商品明细，包括商品名称和小计金额。
    商品名称从关联的 Product 中动态获取（通过 SerializerMethodField），
    小计通过 数量 x 单价 计算。
    """
    # 商品名称，从关联的 Product 对象中动态获取
    product_name = serializers.SerializerMethodField()
    # 小计金额，数量 x 下单时的单价
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'subtotal']

    def get_product_name(self, obj):
        """
        获取商品名称。

        从关联的 Product 对象中获取，即使商品被修改或删除，
        只要 PROTECT 约束允许，就能正确读取。
        """
        return obj.product.name

    def get_subtotal(self, obj):
        """
        计算该明细的小计金额。

        小计 = 购买数量 x 下单时单价。
        使用 price 字段（下单快照价格）而非 product.price（当前价格），
        确保历史订单的金额计算始终准确。
        """
        return obj.quantity * obj.price


class OrderListSerializer(serializers.ModelSerializer):
    """
    订单列表序列化器

    用于订单列表页展示，包含订单的所有核心信息：
    状态、金额、优惠券、收货地址、物流信息以及所有明细。
    嵌套序列化 OrderItemSerializer 展示订单内的商品明细。
    """
    # 嵌套序列化订单中的所有商品明细
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'refund_status', 'total_amount', 'discount_amount', 'coupon', 'address_snapshot', 'tracking_number', 'shipping_method', 'items', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    订单详情序列化器

    用于订单详情页面，在列表字段基础上增加 updated_at 更新时间，
    方便用户追踪订单的完整变更历史。
    refund_status 字段包含退款状态，前端可根据此字段显示退款流程。
    """
    # 嵌套序列化订单中的所有商品明细
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'discount_amount', 'coupon', 'address_snapshot', 'tracking_number', 'shipping_method', 'items', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """
    创建订单请求序列化器

    用于下单接口（POST /orders/place/），验证前端提交的下单请求数据。
    接收用户选中的收货地址 ID、购物车条目 ID 列表和可选的优惠券 ID。

    注意：这不是 ModelSerializer，下单逻辑在 services.create_order 中
    通过数据库事务原子性地完成，序列化器只负责请求数据的验证。
    """
    # 收货地址 ID（必选）
    address_id = serializers.UUIDField()
    # 选中的购物车条目 ID 列表（必选）
    item_ids = serializers.ListField(child=serializers.UUIDField())
    # 优惠券 ID（可选），用户可以不使用优惠券
    coupon_id = serializers.UUIDField(required=False, allow_null=True)

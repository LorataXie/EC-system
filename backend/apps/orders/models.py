from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product


class Order(BaseModel):
    """
    订单主表模型

    存储订单的核心信息，包括用户、金额、优惠券、收货地址快照、
    订单状态、物流信息和退款状态等。

    关键设计决策：
    - address_snapshot: 将收货地址以 JSON 快照形式存储，而非外键关联。
      这样即使用户的地址后期被修改或删除，订单中的历史地址信息依然保留。
    - status 状态流转: pending -> paid -> shipped -> delivered -> completed
                        pending -> cancelled（取消）
    - refund_status: 独立的退款流程状态，与订单主状态并行管理
    - 优惠券外键使用 SET_NULL，优惠券删除后订单仍保留但关联置空
    """
    # 下单用户，使用 PROTECT 防止用户被删除时订单丢失
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', verbose_name='订购用户')
    # 订单总金额（优惠前，即商品原价总和）
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总金额')
    # 优惠券抵扣金额（从 total_amount 中扣除的部分）
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='优惠券抵扣金额')
    # 使用的优惠券，SET_NULL 保证优惠券被删除后订单仍保留
    coupon = models.ForeignKey('coupons.Coupon', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='优惠券')
    # 收货地址快照（JSON 格式），记录下单时的地址信息
    address_snapshot = models.JSONField(default=dict, verbose_name='收货地址快照')
    # 订单状态：pending(待支付) -> paid(已支付) -> shipped(已发货) -> delivered(已送达) -> completed(已完成)
    # cancelled(已取消) 可从 pending 状态直接转入
    status = models.CharField(max_length=20, default='pending', verbose_name='订单状态',
        choices=[('pending', '待支付'), ('paid', '已支付'), ('shipped', '已发货'),
                 ('delivered', '已送达'), ('completed', '已完成'), ('cancelled', '已取消')])
    # 物流单号（发货后填入）
    tracking_number = models.CharField(max_length=100, blank=True, default='', verbose_name='物流单号')
    # 配送方式（如"顺丰快递"）
    shipping_method = models.CharField(max_length=50, blank=True, default='', verbose_name='配送方式')
    # 退款状态：空(无退款) -> requested(申请中) -> approved(已同意) / rejected(已拒绝) -> refunded(已退款)
    refund_status = models.CharField(max_length=20, blank=True, default='', verbose_name='退款状态',
        choices=[('', '无'), ('requested', '申请中'), ('approved', '已同意'), ('rejected', '已拒绝'), ('refunded', '已退款')])

    class Meta:
        db_table = 'orders_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        # 默认按创建时间倒序，最新订单在前
        ordering = ['-created_at']

    def __str__(self):
        # 返回订单编号，便于识别
        return f'Order #{self.id}'


class OrderItem(BaseModel):
    """
    订单明细模型

    记录订单中每个商品的购买信息，包括商品、数量和下单时的单价。
    注意 price 字段是快照价格（下单时的价格），而非关联 Product.price，
    这样即使商品后期调价，历史订单的金额也不会变化。
    """
    # 所属订单，删除订单时级联删除明细
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    # 购买的商品，使用 PROTECT 防止已产生订单的商品被删除
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='商品')
    # 购买数量
    quantity = models.PositiveIntegerField(verbose_name='订购商品数量')
    # 下单时的商品单价（快照价格），不从 Product.price 动态获取
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')

    class Meta:
        db_table = 'orders_order_item'
        verbose_name = '订单明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        # 返回 "商品名 x 数量" 格式
        return f'{self.product.name} x {self.quantity}'

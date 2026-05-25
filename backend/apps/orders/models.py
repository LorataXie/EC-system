from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product


class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', verbose_name='订购用户')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单总金额')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='优惠券抵扣金额')
    coupon = models.ForeignKey('coupons.Coupon', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='优惠券')
    address_snapshot = models.JSONField(default=dict, verbose_name='收货地址快照')
    status = models.CharField(max_length=20, default='pending', verbose_name='订单状态',
        choices=[('pending', '待支付'), ('paid', '已支付'), ('shipped', '已发货'),
                 ('delivered', '已送达'), ('completed', '已完成'), ('cancelled', '已取消')])
    tracking_number = models.CharField(max_length=100, blank=True, default='', verbose_name='物流单号')
    shipping_method = models.CharField(max_length=50, blank=True, default='', verbose_name='配送方式')
    refund_status = models.CharField(max_length=20, blank=True, default='', verbose_name='退款状态',
        choices=[('', '无'), ('requested', '申请中'), ('approved', '已同意'), ('rejected', '已拒绝'), ('refunded', '已退款')])

    class Meta:
        db_table = 'orders_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.PositiveIntegerField(verbose_name='订购商品数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品单价')

    class Meta:
        db_table = 'orders_order_item'
        verbose_name = '订单明细'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

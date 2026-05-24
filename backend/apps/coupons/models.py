from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class Coupon(BaseModel):
    COUPON_TYPES = [
        ('full_reduction', '满减'),
    ]

    type = models.CharField(max_length=20, choices=COUPON_TYPES, verbose_name='优惠券类型')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='优惠券的折扣值')
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='最低订单金额要求')
    start_time = models.DateTimeField(verbose_name='优惠券生效时间')
    end_time = models.DateTimeField(verbose_name='优惠券失效时间')
    status = models.CharField(max_length=20, default='unused', choices=[('unused', '未使用'), ('used', '已使用'), ('expired', '已过期')], verbose_name='优惠券状态')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='coupons', verbose_name='所属用户')

    class Meta:
        db_table = 'coupons_coupon'
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'Coupon #{self.id}'

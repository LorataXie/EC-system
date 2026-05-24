from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product
from apps.orders.models import Order


class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='商品')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='用户')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='订单')
    rating = models.PositiveSmallIntegerField(verbose_name='评分')
    comment = models.TextField(verbose_name='评价内容')
    image = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name='评价图片')

    class Meta:
        db_table = 'reviews_review'
        verbose_name = '商品评价'
        verbose_name_plural = verbose_name
        unique_together = [['user', 'product', 'order']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} 对 {self.product.name} 的评价'

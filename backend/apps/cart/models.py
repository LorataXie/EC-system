from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product


class Cart(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', verbose_name='用户')

    class Meta:
        db_table = 'cart_cart'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.email} 的购物车'


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='购物车')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField(default=1, verbose_name='商品数量')

    class Meta:
        db_table = 'cart_cart_item'
        verbose_name = '购物车商品'
        verbose_name_plural = verbose_name
        unique_together = [['cart', 'product']]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

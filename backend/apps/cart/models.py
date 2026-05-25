from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.products.models import Product


class Cart(BaseModel):
    """
    购物车模型

    每个登录用户有且仅有一个购物车（通过 get_or_create 确保唯一性）。
    购物车本身不存储商品信息，仅作为 CartItem 的容器，
    通过 related_name='items' 可以方便地获取购物车内所有商品条目。
    继承 BaseModel 获得 id、created_at、updated_at 等基础字段。
    """
    # 购物车所属用户，一个用户一个购物车，用户删除时级联删除购物车
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', verbose_name='用户')

    class Meta:
        db_table = 'cart_cart'
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        # 返回 "用户邮箱 的购物车" 格式，便于识别
        return f'{self.user.email} 的购物车'


class CartItem(BaseModel):
    """
    购物车商品条目

    表示购物车中的一件商品及其购买数量。
    通过 unique_together 约束确保同一购物车中同一商品只有一条记录，
    重复添加时会合并数量而不是创建新记录。
    继承 BaseModel 获得 id、created_at、updated_at 等基础字段。
    """
    # 所属购物车，删除购物车时级联删除所有条目
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='购物车')
    # 关联的商品，商品删除时级联删除购物车中的对应条目
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    # 商品数量，最小为1，默认为1
    quantity = models.PositiveIntegerField(default=1, verbose_name='商品数量')

    class Meta:
        db_table = 'cart_cart_item'
        verbose_name = '购物车商品'
        verbose_name_plural = verbose_name
        # 同一购物车中同一商品只能有一条记录，重复添加时合并数量
        unique_together = [['cart', 'product']]

    def __str__(self):
        # 返回 "商品名 x 数量" 格式
        return f'{self.product.name} x {self.quantity}'

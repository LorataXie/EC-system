"""
商品评价模块 - 数据模型 (models)

定义商品评价(Review)的数据结构。

评价系统是电商平台用户反馈体系的核心:
- 帮助其他用户做出购买决策 (社会化证明)
- 为商家提供商品质量反馈
- 评分聚合计算商品平均分 (通过 signal 自动维护)

核心约束:
- 同一用户对同一订单中的同一商品只能评价一次 (unique_together)
- 只能评价已完成的订单 (在视图层校验)
- 评价创建/删除后自动更新商品的 rating_avg 字段 (通过 signals)
"""

from django.db import models
from django.conf import settings
from apps.core.models import BaseModel  # 继承项目基础模型，自动获得时间戳字段
from apps.products.models import Product
from apps.orders.models import Order


class Review(BaseModel):
    """
    商品评价模型

    关联关系:
    - product (FK→Product): 被评价的商品，一对多 (一个商品可被多个用户评价)
    - user (FK→User):       评价者，一对多 (一个用户可评价多个商品)
    - order (FK→Order):     关联订单，用于验证用户确实购买过该商品

    字段说明:
    - rating:  评分 (1-5星)
    - comment: 文字评价内容
    - image:   买家秀图片 (可选上传)
    """

    # =========================================================================
    # 数据库字段定义
    # =========================================================================

    # 被评价的商品
    # related_name='reviews': 通过 product.reviews.all() 获取某商品的所有评价
    # on_delete=CASCADE: 商品删除时级联删除其所有评价 (评价依附于商品存在)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='商品')

    # 评价者
    # related_name='reviews': 通过 user.reviews.all() 获取某用户的所有评价
    # on_delete=CASCADE: 用户删除时级联删除其评价 (避免孤儿数据)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='用户')

    # 关联订单
    # on_delete=PROTECT: 订单删除时保护评价不被级联删除
    # 为何用 PROTECT 而非 CASCADE: 即使订单被删除，商品评价仍有保留价值
    # (比如订单归档清理后，商品评价应该继续展示给后续买家参考)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='订单')

    # 评分: PositiveSmallIntegerField 范围 0-32767，适用于 1-5 的评分场景
    # 不使用 IntegerField 是为了节省存储空间 (2字节 vs 4字节)
    rating = models.PositiveSmallIntegerField(verbose_name='评分')

    # 评价文字内容: TextField 无长度限制，适合用户长篇评价
    comment = models.TextField(verbose_name='评价内容')

    # 评价图片: ImageField 会自动处理文件上传和存储路径
    # - upload_to='reviews/': 图片存储在 MEDIA_ROOT/reviews/ 目录下
    # - blank=True, null=True: 图片为可选字段，允许纯文字评价
    image = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name='评价图片')

    class Meta:
        # 数据库表名: 显式指定，避免 Django 自动命名不一致
        db_table = 'reviews_review'
        # Django Admin 中的显示名
        verbose_name = '商品评价'
        verbose_name_plural = verbose_name

        # 唯一约束: 同一用户不能对同一订单的同一商品重复评价
        # 防止用户刷评价、提交重复数据
        # Django 会在数据库层面创建联合唯一索引
        unique_together = [['user', 'product', 'order']]

        # 默认排序: 最新评价在前，用户查看商品评价时优先看到最近的反馈
        ordering = ['-created_at']

    def __str__(self):
        """对象的可读字符串表示，Admin 和调试中使用"""
        return f'{self.user.email} 对 {self.product.name} 的评价'

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from apps.core.models import BaseModel


class Category(MPTTModel, BaseModel):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        db_table = 'products_category'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=200, verbose_name='商品名称')
    description = models.TextField(verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    stock = models.PositiveIntegerField(default=0, verbose_name='商品库存')
    sales_count = models.PositiveIntegerField(default=0, verbose_name='销量')
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name='平均评分')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='所属分类')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='商品图片')

    class Meta:
        db_table = 'products_product'
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

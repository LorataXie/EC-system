from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from apps.core.models import BaseModel


class Category(MPTTModel, BaseModel):
    """
    商品分类模型（MPTT 树形结构）

    使用 django-mptt 实现多级分类树，支持无限层级嵌套。
    每个分类可以有一个父分类，形成树形层级关系。
    继承 BaseModel 获得 id、created_at、updated_at 等基础字段。
    """
    # 分类名称，用于展示如"手机"、"电脑"、"服装"等
    name = models.CharField(max_length=100, verbose_name='分类名称')
    # 父分类外键，指向自身形成树形结构；null 表示根分类
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父分类')

    class MPTTMeta:
        # 同一层级下按名称排序插入
        order_insertion_by = ['name']

    class Meta:
        db_table = 'products_category'
        verbose_name = '商品分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        # 返回分类名称，用于 Django Admin 等展示
        return self.name


class Product(BaseModel):
    """
    商品模型

    存储商品的核心信息，包括名称、描述、价格、库存、销量、评分等。
    每个商品属于一个分类（Category），通过外键关联。
    继承 BaseModel 获得 id、created_at、updated_at 等基础字段。
    """
    # 商品名称，限制200字符
    name = models.CharField(max_length=200, verbose_name='商品名称')
    # 商品描述，使用 TextField 支持长文本
    description = models.TextField(verbose_name='商品描述')
    # 商品价格，使用 DecimalField 精确存储金额（最大10位，2位小数）
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    # 商品库存，使用 PositiveIntegerField 确保不为负
    stock = models.PositiveIntegerField(default=0, verbose_name='商品库存')
    # 累计销量，用于前台展示热销程度
    sales_count = models.PositiveIntegerField(default=0, verbose_name='销量')
    # 平均评分，保留2位小数（范围 0.00 ~ 5.00）
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name='平均评分')
    # 所属分类，使用 PROTECT 防止误删有商品的分类
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name='所属分类')
    # 商品图片，上传到 media/products/ 目录，可为空
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='商品图片')

    class Meta:
        db_table = 'products_product'
        verbose_name = '商品'
        verbose_name_plural = verbose_name
        # 默认按创建时间倒序排列，最新商品在前
        ordering = ['-created_at']

    def __str__(self):
        # 返回商品名称，用于 Django Admin 等展示
        return self.name

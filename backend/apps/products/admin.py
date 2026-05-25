from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """
    Django Admin 分类管理配置

    使用 MPTTModelAdmin 而不是普通 ModelAdmin，以便在管理后台中
    以树形层级结构展示分类列表，支持拖拽排序和层级管理。
    """
    # 列表页显示的列：分类名称和父分类
    list_display = ['name', 'parent']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Django Admin 商品管理配置

    在管理后台中提供商品的列表查看和搜索功能。
    """
    # 列表页显示的列：名称、所属分类、价格、库存
    list_display = ['name', 'category', 'price', 'stock']
    # 允许按商品名称和描述进行搜索
    search_fields = ['name', 'description']

from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'parent']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock']
    search_fields = ['name', 'description']

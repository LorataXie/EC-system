"""
账户模块 - Django Admin 后台配置

将自定义的 User 和 Address 模型注册到 Django 自带的管理后台，
方便运维人员直接在浏览器中进行数据管理和查看。
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    自定义用户管理界面。

    继承 Django 内置的 UserAdmin，保留原有的权限管理、密码修改等功能，
    同时添加电商特有的字段（手机号、VIP状态等）到列表和编辑表单。
    """

    # 列表页显示的列：邮箱、用户名、手机号、VIP、员工、激活状态、注册时间
    list_display = ['email', 'username', 'phone', 'is_vip', 'is_staff', 'is_active', 'date_joined']

    # 搜索框可搜索的字段：按邮箱、用户名或手机号查找用户
    search_fields = ['email', 'username', 'phone']

    # 默认排序：最新注册的用户排在最前面
    ordering = ['-date_joined']

    # fieldsets：详情页字段分组
    # 在 Django 内置字段分组基础上追加"额外信息"分组，包含电商特有的用户字段
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('phone', 'age', 'gender', 'is_vip')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    收货地址管理界面。

    提供收货地址的列表查看功能，展示关键字段方便客服和管理员
    快速定位用户地址信息。
    """

    # 列表页显示的列：用户、收货人、电话、省份、城市、是否默认地址
    list_display = ['user', 'recipient_name', 'phone', 'state', 'city', 'is_default']

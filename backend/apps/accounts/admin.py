from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'phone', 'is_vip', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'phone']
    ordering = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('phone', 'age', 'gender', 'is_vip')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipient_name', 'phone', 'state', 'city', 'is_default']

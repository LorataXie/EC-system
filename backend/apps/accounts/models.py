from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name='手机号')
    age = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='年龄')
    gender = models.CharField(max_length=10, blank=True, default='', verbose_name='性别')
    is_vip = models.BooleanField(default=False, verbose_name='VIP用户')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    recipient_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    phone = models.CharField(max_length=20, verbose_name='收货人电话')
    address_line1 = models.CharField(max_length=255, verbose_name='地址行1')
    address_line2 = models.CharField(max_length=255, blank=True, default='', verbose_name='地址行2')
    city = models.CharField(max_length=50, verbose_name='城市')
    state = models.CharField(max_length=50, verbose_name='省份/州')
    postal_code = models.CharField(max_length=10, blank=True, default='', verbose_name='邮政编码')
    country = models.CharField(max_length=50, blank=True, default='中国', verbose_name='国家')
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    class Meta:
        db_table = 'accounts_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.recipient_name} - {self.state}{self.city}'


class OperationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs', verbose_name='用户')
    action = models.CharField(max_length=50, verbose_name='操作')
    detail = models.TextField(blank=True, default='', verbose_name='详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'accounts_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

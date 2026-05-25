"""
账户模块 - 数据模型

定义用户、收货地址和操作日志三个核心模型。
用户模型扩展了 Django 的 AbstractUser，使用邮箱作为登录凭证而非用户名，
这是现代 Web 应用的常见做法（邮箱唯一性好、便于找回密码）。
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import BaseModel


class User(AbstractUser):
    """
    自定义用户模型，继承 Django 的 AbstractUser 并扩展电商场景需要的字段。

    关键设计决策——为什么用邮箱登录：
    1. 邮箱天然唯一，比用户名更适合作为登录凭证
    2. 邮箱可用于密码找回、订单通知等业务场景，用户名无法做到
    3. 手机号也可登录（通过 phone 字段），提供多种登录方式

    USERNAME_FIELD = 'email' 告诉 Django 认证系统用邮箱代替用户名进行身份验证。
    但 Django 底层仍需 username 字段（AbstractUser 强依赖），因此保留了 username，
    注册时由用户提供或由系统自动生成。
    """

    # 邮箱作为登录凭证，unique=True 确保账号唯一性
    email = models.EmailField(unique=True, verbose_name='邮箱')

    # 手机号：可用于手机号登录、短信通知、物流联系等场景
    # blank=True 允许为空，因为邮箱注册的用户可能不填手机号
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name='手机号')

    # 年龄：用于用户画像分析、个性化推荐
    age = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='年龄')

    # 性别：用于商品推荐（如服饰类商品按性别推荐）
    gender = models.CharField(max_length=10, blank=True, default='', verbose_name='性别')

    # VIP 标识：控制会员专属权益，如折扣价、免运费等
    is_vip = models.BooleanField(default=False, verbose_name='VIP用户')

    # 指定用于认证的字段为 email，Django 的 authenticate() 会据此验证用户
    USERNAME_FIELD = 'email'

    # createsuperuser 管理命令会额外要求填写的字段
    REQUIRED_FIELDS = ['username']

    class Meta:
        # 指定数据库表名，避免使用默认的 app_label_model 格式
        db_table = 'accounts_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        """返回用户的邮箱地址作为可读标识"""
        return self.email


class Address(BaseModel):
    """
    用户收货地址，继承 BaseModel 获得 UUID 主键和时间戳。

    一个用户可以拥有多个收货地址（通过 ForeignKey 关联），
    其中一个可以被标记为默认地址（is_default=True）。
    地址以中国为主要市场，country 默认值为"中国"。
    """

    # 关联用户：CASCADE 删除表示用户被删除时其所有地址也被删除
    # related_name='addresses' 允许通过 user.addresses.all() 获取用户的所有地址
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')

    # 收货人姓名：快递和物流环节必需
    recipient_name = models.CharField(max_length=50, verbose_name='收货人姓名')

    # 收货人电话：快递员联系收件人使用
    phone = models.CharField(max_length=20, verbose_name='收货人电话')

    # 地址行1：存放详细地址（如"XX路XX号XX小区3栋501"）
    address_line1 = models.CharField(max_length=255, verbose_name='地址行1')

    # 地址行2：补充地址信息（如"靠近地铁站A出口"），非必填
    address_line2 = models.CharField(max_length=255, blank=True, default='', verbose_name='地址行2')

    # 城市：用于物流路由规划
    city = models.CharField(max_length=50, verbose_name='城市')

    # 省份/州：用于物流路由规划
    state = models.CharField(max_length=50, verbose_name='省份/州')

    # 邮政编码：辅助物流分拣

    postal_code = models.CharField(max_length=10, blank=True, default='', verbose_name='邮政编码')

    # 国家：默认为"中国"
    country = models.CharField(max_length=50, blank=True, default='中国', verbose_name='国家')

    # 默认地址标识：用户下单时默认选择此项地址
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    class Meta:
        db_table = 'accounts_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        # 排序规则：默认地址优先显示，其次按创建时间倒序
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        """返回"收货人 - 省份城市"格式的可读标识"""
        return f'{self.recipient_name} - {self.state}{self.city}'


class OperationLog(models.Model):
    """
    用户操作日志，记录用户的关键操作行为。

    设计目的：
    1. 安全审计：追踪敏感操作（如修改密码、修改权限）
    2. 客服支持：查看用户历史操作，帮助排查问题
    3. 数据分析：统计用户行为模式

    注意：此模型不继承 BaseModel，仅需 created_at 字段（操作时间），
    不需要 UUID 主键和 updated_at（操作日志一旦记录就不应修改）。
    """

    # 关联用户：记录是哪个用户执行的操作
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs', verbose_name='用户')

    # 操作类型：简短的分类标签，如"修改密码"、"管理员修改"、"下单"
    action = models.CharField(max_length=50, verbose_name='操作')

    # 操作详情：更具体的描述，如"is_vip: False -> True; is_active: True -> False"
    detail = models.TextField(blank=True, default='', verbose_name='详情')

    # 操作时间：记录操作发生的精确时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'accounts_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        # 按时间倒序，最新的操作显示在最前面
        ordering = ['-created_at']

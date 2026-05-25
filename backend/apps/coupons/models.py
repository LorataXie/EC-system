"""
优惠券模块 - 数据模型 (models)

定义优惠券(Coupon)的数据结构，包括:
- 优惠券类型 (目前仅支持满减)
- 折扣金额、最低消费门槛
- 有效期范围
- 使用状态 (未使用/已使用/已过期)
- 所属用户关联

优惠券系统是电商营销体系的核心组件，用于:
- 刺激用户下单 (满减门槛)
- 提升客单价 (最低消费限制)
- 控制营销成本 (有效期限制)
"""

from django.conf import settings
from django.db import models
from apps.core.models import BaseModel  # 继承项目基础模型，自动获得 created_at/updated_at 时间戳字段


class Coupon(BaseModel):
    """
    优惠券模型

    每张优惠券与一个用户绑定 (可为空，用于预生成未分配的券)，
    核心字段说明:
    - type: 优惠券类型，目前仅支持 'full_reduction' (满减)
    - discount_value: 优惠金额 (元)，满减时为用户减免的具体金额
    - min_order_amount: 最低订单金额门槛，订单总价低于此金额则无法使用该券
    - start_time / end_time: 券的有效时间窗口，过期后自动标记为 expired
    - status: 生命周期状态 (unused → used/expired)
    """

    # =========================================================================
    # 优惠券类型选择项
    # 采用元组列表定义 choices，第一个值为数据库存储值，第二个值为前端展示的中文名
    # 目前仅支持 '满减' 一种类型，后续可扩展 '折扣'、'固定金额' 等
    # =========================================================================
    COUPON_TYPES = [
        ('full_reduction', '满减'),
    ]

    # =========================================================================
    # 数据库字段定义
    # =========================================================================

    # 优惠券类型: 使用 CharField + choices 限制取值，保证数据一致性
    type = models.CharField(max_length=20, choices=COUPON_TYPES, verbose_name='优惠券类型')

    # 折扣金额: 使用 DecimalField 而非 FloatField，避免浮点精度问题 (如 0.1+0.2!=0.3)
    # max_digits=10 指总位数 (含小数)，decimal_places=2 指保留2位小数，即最多 99999999.99
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='优惠券的折扣值')

    # 最低订单金额: 订单总价需 >= 此值才能使用该优惠券，默认为 0 表示无门槛
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='最低订单金额要求')

    # 生效时间: 优惠券可开始使用的时间点
    start_time = models.DateTimeField(verbose_name='优惠券生效时间')

    # 失效时间: 优惠券过期的时间点，超过此时间即不可使用
    end_time = models.DateTimeField(verbose_name='优惠券失效时间')

    # 使用状态: 跟踪每张券的生命周期
    # - 'unused':  未使用，可正常使用
    # - 'used':    已使用 (在下单时标记)
    # - 'expired': 已过期 (超过 end_time 自动标记)
    status = models.CharField(
        max_length=20,
        default='unused',
        choices=[('unused', '未使用'), ('used', '已使用'), ('expired', '已过期')],
        verbose_name='优惠券状态'
    )

    # 所属用户: ForeignKey 关联自定义用户模型
    # - null=True, blank=True: 允许券不绑定用户 (如管理员批量生成的未分配优惠券)
    # - related_name='coupons': 通过 user.coupons 反向查询该用户的所有优惠券
    # - on_delete=CASCADE: 用户删除时级联删除其优惠券
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='coupons',
        verbose_name='所属用户'
    )

    class Meta:
        # 数据库表名: 显式指定避免 Django 自动生成的 app_label_model 格式不一致
        db_table = 'coupons_coupon'
        # Django Admin 中显示的模型名称
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name

    def __str__(self):
        """对象的字符串表示，在 Django Admin 和调试中使用"""
        return f'Coupon #{self.id}'

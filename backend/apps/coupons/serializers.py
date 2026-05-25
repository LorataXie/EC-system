"""
优惠券模块 - 序列化器 (serializers)

定义优惠券数据的序列化/反序列化规则，负责:
- 将 Model 对象转换为 JSON 响应 (序列化)
- 将请求 JSON 数据验证并转换为 Model 对象 (反序列化)
- 控制不同场景下暴露的字段 (列表/详情 vs 创建)

包含三个序列化器:
1. CouponSerializer:      普通用户查看优惠券列表/详情时使用
2. CouponCreateSerializer: 管理员创建单张优惠券时使用
3. CouponIssueSerializer:  管理员批量发放优惠券时的请求参数校验
"""

from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """
    优惠券序列化器 (读取场景)

    用于普通用户查看自己的优惠券列表和详情。
    额外暴露 user_email 只读字段，方便前端展示而不需要额外请求用户信息。
    所有字段标记为只读，确保此序列化器仅用于 GET 响应。
    """
    # 通过 source='user.email' 跨关联对象取值，将外键关联的用户邮箱直接暴露到 JSON 中
    # read_only=True 表示该字段仅用于输出，不参与反序列化验证
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Coupon
        # 明确列出所有输出字段
        fields = ['id', 'type', 'discount_value', 'min_order_amount',
                  'start_time', 'end_time', 'status', 'user', 'user_email', 'created_at']
        # id 和 created_at 由系统自动生成，不允许客户端修改
        read_only_fields = ['id', 'created_at']


class CouponCreateSerializer(serializers.ModelSerializer):
    """
    优惠券创建序列化器 (写入场景)

    用于管理员通过 Admin API 创建单张优惠券。
    与 CouponSerializer 的区别:
    - 不包含 user_email 只读字段 (创建时无需展示)
    - 大部分字段可写，仅 id 和 created_at 为只读
    """

    class Meta:
        model = Coupon
        fields = ['id', 'type', 'discount_value', 'min_order_amount',
                  'start_time', 'end_time', 'status', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class CouponIssueSerializer(serializers.Serializer):
    """
    优惠券批量发放序列化器 (纯请求参数校验)

    用于管理员批量向多个用户发放优惠券的请求参数验证。
    不绑定 Model，继承自 Serializer 而非 ModelSerializer，
    因为其数据结构与 Coupon 模型不是简单的一对一映射关系:
    - 一个请求可创建多张券 (user_ids × count_per_user)
    - 每张券单独 insert 到数据库

    字段说明:
    - user_ids:         接收优惠券的用户 ID 列表
    - type:             统一类型
    - discount_value:   统一面额
    - min_order_amount: 统一使用门槛
    - start_time/end_time: 统一有效期
    - count_per_user:   每个用户发放张数，默认1张
    """
    # ListField + IntegerField: 接收整型数组，如 [1, 2, 3]
    user_ids = serializers.ListField(child=serializers.IntegerField())

    # ChoiceField 使用模型的 COUPON_TYPES 常量，保证前端传值与数据库一致
    type = serializers.ChoiceField(choices=Coupon.COUPON_TYPES)

    # DecimalField: 金额字段同样用 Decimal 保证精度
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)

    # 默认值为 0 表示无门槛券
    min_order_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

    # DateTimeField: DRF 自动处理 ISO 8601 日期字符串的解析
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    # min_value=1: 每个用户至少发1张，避免无效请求
    count_per_user = serializers.IntegerField(default=1, min_value=1)

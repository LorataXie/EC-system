"""
商品评价模块 - 序列化器 (serializers)

定义评价数据的序列化/反序列化规则。

两个序列化器:
1. ReviewSerializer:       读取场景 (列表/详情)，展示丰富的关联信息
2. ReviewCreateSerializer: 创建场景，只需提交核心字段，user 由服务端自动注入
"""

from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    评价序列化器 (读取场景)

    用于评价列表和详情的 JSON 输出。
    通过 source 参数跨表提取关联字段，减少前端的额外请求:
    - product_name: 商品名称 (无需前端再调 products API)
    - user_name:    用户名 (无需前端再调 accounts API)
    """

    # 通过 source='product.name' 从关联的 Product 对象中提取商品名
    # read_only=True: 该字段仅用于输出，写入时不接受此字段
    product_name = serializers.CharField(source='product.name', read_only=True)

    # 通过 source='user.username' 从关联的 User 对象中提取用户名
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        # 明确列出所有输出字段
        fields = ['id', 'product', 'product_name', 'user', 'user_name',
                  'order', 'rating', 'comment', 'image', 'created_at']
        # id 和 user 由系统自动生成，不允许客户端修改
        # user 在 create 时由 perform_create 注入，而非从请求数据中取 (防止伪造)
        read_only_fields = ['id', 'user', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    评价创建序列化器 (写入场景)

    用于接收用户提交的评价数据。
    设计要点:
    - 不包含 user 字段: 由视图层的 perform_create 从 request.user 注入，
      防止用户伪造他人身份提交评价
    - 字段集精简: 只包含用户可填写的字段 (商品、订单、评分、内容、图片)
    - 不包含只读字段: id、created_at 由系统自动管理
    """

    class Meta:
        model = Review
        fields = ['product', 'order', 'rating', 'comment', 'image']

    def create(self, validated_data):
        """
        重写 create 方法，自动注入当前登录用户作为评价者

        为何在这里注入而非在视图中: 这是 DRF 的最佳实践，
        将用户注入逻辑封装在序列化器中，保持视图层简洁。

        self.context['request'].user: 从 DRF 上下文获取当前请求用户
        (DRF 在调用 serializer.save() 时会自动传入 request 到 context 中)
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

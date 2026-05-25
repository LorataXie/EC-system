"""
商品评价模块 - 视图 (views)

定义评价相关的 API 端点。

两个视图集:
1. ReviewViewSet:      面向所有用户 (浏览评价) 和已登录用户 (创建/编辑/删除评价)
2. ReviewAdminViewSet: 管理员接口 (查看所有评价、删除违规评价)

核心业务规则:
- 任何人都可以查看评价 (AllowAny)
- 只有已登录用户可以创建评价，且只能评价已完成的订单
- 只有评价者本人或管理员可以修改/删除评价
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from apps.core.permissions import IsOwnerOrAdmin, IsAdminUser


class ReviewViewSet(viewsets.ModelViewSet):
    """
    商品评价 ViewSet (完整 CRUD)

    继承 ModelViewSet，自动提供:
    - GET    /reviews             — 评价列表 (支持按 product_id/order_id 筛选)
    - POST   /reviews             — 创建评价 (需登录)
    - GET    /reviews/{id}        — 评价详情
    - PUT    /reviews/{id}        — 完整更新 (仅本人/管理员)
    - PATCH  /reviews/{id}        — 部分更新 (仅本人/管理员)
    - DELETE /reviews/{id}        — 删除评价 (仅本人/管理员)

    权限策略 (由 get_permissions 动态分配):
    - list/retrieve:   所有人可访问 (帮助未登录用户查看商品评价)
    - create:          需登录
    - update/destroy:  需登录 + 是评价者或管理员
    """

    # 使用 select_related 预加载 user 和 product，减少 N+1 查询
    queryset = Review.objects.select_related('user', 'product')

    # 基础权限: 默认允许任何人查看评价
    # 具体操作的权限由 get_permissions 方法动态覆盖
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """
        根据 action 动态选择序列化器

        - create: 使用 ReviewCreateSerializer (不需要 user 字段输入)
        - 其他:   使用 ReviewSerializer (包含 product_name, user_name 等展示字段)
        """
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        """
        根据 action 动态分配权限

        为何这样设计: 不同操作有不同的权限需求:
        - 查看评价: 对所有人开放，提升商品详情页的转化率 (社会化证明)
        - 创建评价: 需要登录，防止匿名恶意评价
        - 编辑/删除: 只有评价者本人或管理员可以操作，防止数据被他人篡改
        """
        if self.action == 'create':
            # 创建评价需要登录 (JWT 认证)
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            # 修改/删除需要登录 + 是评价者本人或管理员
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        # list 和 retrieve 保持默认的 AllowAny
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        创建评价前的业务校验

        校验逻辑:
        1. 订单必须存在且属于当前用户 (防止伪造订单号评价)
        2. 订单状态必须为 'completed' (只有已完成的订单才能评价)
           - 为何这样限制: 防止用户收到货前随意评价，保证评价真实性

        校验通过后才执行 serializer.save() 写入数据库
        """
        from apps.orders.models import Order  # 延迟导入避免循环引用

        # 从请求数据中提取订单 ID
        order_id = self.request.data.get('order')
        user = self.request.user

        # 校验1: 订单存在性 + 归属校验 (一次查询完成两项检查)
        # filter(id=order_id, user=user): 同时验证订单ID和归属，防止用户评价他人订单
        order = Order.objects.filter(id=order_id, user=user).first()
        if not order:
            raise serializers.ValidationError({'order': '订单不存在'})

        # 校验2: 订单必须是已完成状态
        # 只有已完成的订单才能评价，避免用户对未支付/未发货的订单进行评价
        if order.status != 'completed':
            raise serializers.ValidationError({'order': '只能评价已完成的订单'})

        # 校验通过，调用序列化器的 save 方法写入数据库
        serializer.save()

    def get_queryset(self):
        """
        支持按商品ID和订单ID筛选评价列表

        使用场景:
        - ?product_id=1: 商品详情页展示该商品的所有评价
        - ?order_id=5:   用户查看某个订单下的评价

        为何重写 get_queryset 而非使用 DRF FilterBackend:
        这里是简单查询参数筛选，直接在 queryset 层处理更轻量高效
        """
        qs = super().get_queryset()

        # 按商品筛选
        product_id = self.request.query_params.get('product_id')
        if product_id:
            qs = qs.filter(product_id=product_id)

        # 按订单筛选
        order_id = self.request.query_params.get('order_id')
        if order_id:
            qs = qs.filter(order_id=order_id)

        return qs


class ReviewAdminViewSet(viewsets.GenericViewSet):
    """
    管理员评价接口

    使用 GenericViewSet 而非 ModelViewSet，因为管理员不需要标准 CRUD，
    只需要两个自定义端点:
    - GET /admin/reviews/all:    查看所有评价 (带分页)
    - DELETE /admin/reviews/{id}/remove: 删除违规评价

    权限: JWT 认证 + 管理员角色
    """

    # 双重权限: JWT + 管理员角色
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    # 基础查询集
    queryset = Review.objects.all()

    @action(methods=['get'], detail=False)
    def all(self, request):
        """
        管理员查看所有评价列表 (带分页)

        GET /api/v1/admin/reviews/all

        与普通用户接口的区别:
        - 管理员能看到所有用户的评价 (不做 user 筛选)
        - 带分页支持，避免大量数据一次返回导致性能问题
        - 预加载 user 和 product 避免 N+1 查询
        """
        # select_related 预加载关联数据，减少数据库查询次数
        qs = self.queryset.select_related('user', 'product')

        # DRF 分页: paginate_queryset 将查询集切分为当前页数据
        page = self.paginate_queryset(qs)
        if page is not None:
            # get_paginated_response 返回包含分页元数据的标准格式响应
            # 格式: { "count": 100, "next": "...", "previous": "...", "results": [...] }
            return self.get_paginated_response(ReviewSerializer(page, many=True).data)

        # 如果没有启用分页 (理论上不会发生)，返回全量数据
        return Response(ReviewSerializer(qs, many=True).data)

    @action(methods=['delete'], detail=True)
    def remove(self, request, pk=None):
        """
        管理员删除指定评价

        DELETE /api/v1/admin/reviews/{id}/remove

        为何单独命名为 remove 而非重写 destroy:
        - 语义更明确: remove 表示"移除违规内容"，destroy 泛化度较高
        - 便于后续添加删除前的审核流程 (如记录删除原因、通知用户等)

        删除后 Django 的 post_delete signal 会自动触发
        update_product_rating 更新商品平均评分 (见 signals.py)
        """
        self.queryset.get(id=pk).delete()
        # 204 No Content: 删除成功，无响应体
        return Response(status=status.HTTP_204_NO_CONTENT)

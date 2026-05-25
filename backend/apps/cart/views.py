from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddCartItemSerializer,
    UpdateCartItemSerializer, BatchDeleteSerializer,
)
from .services import get_or_create_cart
from apps.products.models import Product


class CartViewSet(viewsets.GenericViewSet):
    """
    购物车视图集

    提供购物车的完整操作接口，所有操作都需要用户登录。
    核心功能包括：
    - my: 查看我的购物车（列表及总金额）
    - add_item: 添加商品到购物车（重复添加自动合并数量）
    - manage_item: 更新/删除单个购物车条目（PATCH 修改数量，DELETE 删除）
    - batch_delete: 批量删除购物车条目

    关键设计决策：
    - 自动获取或创建购物车（懒加载），用户首次操作时自动创建
    - 添加商品时自动校验库存上限，不允许超过库存
    - 重复添加同一商品时合并数量而非创建新记录
    """
    # 所有操作都需要登录
    permission_classes = [permissions.IsAuthenticated]

    def _get_cart(self):
        """
        获取或创建当前用户的购物车。

        通过 services.get_or_create_cart 实现懒加载：
        用户首次访问购物车时自动创建，后续操作复用已有购物车。
        封装为私有方法避免在每个 action 中重复调用。
        """
        return get_or_create_cart(user=self.request.user)

    @action(methods=['get'], detail=False)
    def my(self, request):
        """
        获取当前用户的购物车完整信息。

        返回购物车中的所有商品条目、总金额和商品种类数。
        前端购物车页面通过此接口获取并渲染购物车内容。
        """
        cart = self._get_cart()
        return Response(CartSerializer(cart).data)

    @action(methods=['post'], detail=False, url_path='items')
    def add_item(self, request):
        """
        向购物车中添加商品。

        处理逻辑：
        1. 验证请求数据（商品 ID 和数量）
        2. 获取或创建当前用户的购物车
        3. 查找商品是否存在
        4. 如果购物车中已有该商品，则合并数量（不超过库存）
        5. 如果是新商品，则创建条目（数量不超过库存）
        6. 已存在返回 200，新创建返回 201

        关键保护：数量始终不超过商品库存，防止超卖。
        """
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self._get_cart()
        product = get_object_or_404(Product, id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']

        # 尝试获取已有条目或创建新条目
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': min(quantity, product.stock)}
        )
        if not created:
            # 已有条目：合并数量，但不能超过库存上限
            item.quantity = min(item.quantity + quantity, product.stock)
            item.save(update_fields=['quantity'])

        # 根据是否新创建返回不同的 HTTP 状态码
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(methods=['patch', 'delete'], detail=False, url_path='items/(?P<item_id>[^/.]+)')
    def manage_item(self, request, item_id=None):
        """
        管理单个购物车条目：更新数量或删除。

        PATCH 请求：更新商品数量（限制不超过库存）
        DELETE 请求：从购物车中移除该商品

        通过 item_id 定位条目，并校验条目属于当前用户的购物车，
        防止用户操作他人的购物车。
        """
        cart = self._get_cart()
        # 确保条目属于当前用户的购物车
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if request.method == 'PATCH':
            # 更新数量：不能超过商品当前库存
            serializer = UpdateCartItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            item.quantity = min(serializer.validated_data['quantity'], item.product.stock)
            item.save(update_fields=['quantity'])
            return Response(CartItemSerializer(item).data)

        # DELETE：删除条目
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='items/batch-delete')
    def batch_delete(self, request):
        """
        批量删除购物车中的多个商品条目。

        接收一个 item_ids 列表，一次性删除多个条目。
        相比前端逐个调用删除接口，批量操作减少了网络请求次数，
        提升了用户体验，特别是用户需要清空购物车或删除多个商品时。

        安全性：只删除属于当前用户购物车的条目，
        用户不能删除他人购物车中的商品。
        """
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self._get_cart()
        # 只删除属于当前用户购物车的条目，过滤掉其他用户的 ID
        cart.items.filter(id__in=serializer.validated_data['item_ids']).delete()
        return Response({'detail': 'ok'})

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
    permission_classes = [permissions.IsAuthenticated]

    def _get_cart(self):
        return get_or_create_cart(user=self.request.user)

    @action(methods=['get'], detail=False)
    def my(self, request):
        cart = self._get_cart()
        return Response(CartSerializer(cart).data)

    @action(methods=['post'], detail=False, url_path='items')
    def add_item(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self._get_cart()
        product = get_object_or_404(Product, id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': min(quantity, product.stock)}
        )
        if not created:
            item.quantity = min(item.quantity + quantity, product.stock)
            item.save(update_fields=['quantity'])
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(methods=['patch', 'delete'], detail=False, url_path='items/(?P<item_id>[^/.]+)')
    def manage_item(self, request, item_id=None):
        cart = self._get_cart()
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if request.method == 'PATCH':
            serializer = UpdateCartItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            item.quantity = min(serializer.validated_data['quantity'], item.product.stock)
            item.save(update_fields=['quantity'])
            return Response(CartItemSerializer(item).data)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False, url_path='items/batch-delete')
    def batch_delete(self, request):
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self._get_cart()
        cart.items.filter(id__in=serializer.validated_data['item_ids']).delete()
        return Response({'detail': 'ok'})

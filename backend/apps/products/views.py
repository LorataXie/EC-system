from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import (
    CategorySerializer, CategoryFlatSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductAdminSerializer,
)
from .filters import ProductFilter
from apps.core.permissions import IsAdminUser


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'list':
            flat = self.request.query_params.get('flat', 'false').lower() == 'true'
            return CategoryFlatSerializer if flat else CategorySerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        flat = request.query_params.get('flat', 'false').lower() == 'true'
        if flat:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        roots = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(roots, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('category').all()
    lookup_field = 'pk'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer


class ProductAdminViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class CategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryFlatSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

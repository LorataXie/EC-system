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
    """
    分类视图集（只读）

    提供分类的列表和详情查询接口。
    支持两种模式：
    - 树形模式（默认）：以嵌套树形结构返回分类，顶层为根分类
    - 扁平模式（flat=true）：以扁平列表返回所有分类，方便下拉选择
    """
    queryset = Category.objects.all()
    lookup_field = 'pk'

    def get_serializer_class(self):
        """
        根据请求参数动态选择序列化器。

        flat=true 时使用扁平序列化器（适合下拉列表），
        否则使用树形序列化器（适合导航菜单）。
        """
        if self.action == 'list':
            flat = self.request.query_params.get('flat', 'false').lower() == 'true'
            return CategoryFlatSerializer if flat else CategorySerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        """
        自定义列表方法，支持树形和扁平两种输出模式。

        扁平模式：返回所有分类的扁平列表，每个分类附带父分类名称。
        树形模式：只返回根分类（parent 为 null），通过 CategorySerializer
                  的递归嵌套自动构建完整树结构。
        这样设计是为了让前端可以根据场景灵活选择数据格式。
        """
        flat = request.query_params.get('flat', 'false').lower() == 'true'
        if flat:
            # 扁平模式：返回所有分类
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        # 树形模式：只取根节点，由序列化器递归生成树
        roots = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(roots, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    商品视图集（只读，面向普通用户）

    提供商品的列表搜索和详情查看接口。
    列表接口支持按关键字、分类、价格区间筛选以及多种排序方式。
    使用 select_related 预加载分类信息，避免 N+1 查询。
    """
    # 预加载 category 外键关联，减少数据库查询次数
    queryset = Product.objects.select_related('category').all()
    lookup_field = 'pk'
    # 启用 DjangoFilterBackend 进行条件过滤
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        """
        根据操作类型动态选择序列化器。

        列表操作使用 ProductListSerializer（字段精简），
        详情操作使用 ProductDetailSerializer（包含完整描述）。
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer


class ProductAdminViewSet(viewsets.ModelViewSet):
    """
    管理员商品视图集（完整 CRUD）

    仅管理员可访问，支持对商品进行创建、读取、更新、删除等全部操作。
    使用 ProductAdminSerializer 暴露所有字段。
    """
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductAdminSerializer
    # 需要登录且为管理员身份
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class CategoryAdminViewSet(viewsets.ModelViewSet):
    """
    管理员分类视图集（完整 CRUD）

    仅管理员可访问，支持对分类进行创建、读取、更新、删除等全部操作。
    使用 CategoryFlatSerializer 以扁平结构管理分类。
    """
    queryset = Category.objects.all()
    serializer_class = CategoryFlatSerializer
    # 需要登录且为管理员身份
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

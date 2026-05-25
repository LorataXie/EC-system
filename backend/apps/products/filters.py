import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    商品过滤器

    为商品列表接口提供多维度的筛选功能，支持：
    - keyword: 按商品名称模糊搜索
    - category: 按分类 ID 精确筛选
    - min_price / max_price: 按价格区间筛选
    - sort: 按价格、时间、销量排序

    这些筛选条件都可以自由组合使用，前端将筛选参数作为查询字符串传递。
    """
    # 关键字搜索：模糊匹配商品名称（使用自定义方法 filter_keyword）
    keyword = django_filters.CharFilter(method='filter_keyword')
    # 按分类 ID 精确筛选
    category = django_filters.UUIDFilter(field_name='category_id', lookup_expr='exact')
    # 最低价格：筛选价格 >= min_price 的商品
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    # 最高价格：筛选价格 <= max_price 的商品
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    # 排序方式：由自定义方法 filter_sort 处理
    sort = django_filters.CharFilter(method='filter_sort')

    class Meta:
        model = Product
        # 基础筛选字段
        fields = ['category', 'min_price', 'max_price']

    def filter_keyword(self, queryset, name, value):
        """
        按关键字模糊搜索商品名称。

        使用 icontains 实现不区分大小写的模糊匹配，
        用户输入的关键字会匹配商品名称中任意位置的子串。
        """
        return queryset.filter(name__icontains=value)

    def filter_sort(self, queryset, name, value):
        """
        按指定规则对商品列表排序。

        支持的排序方式：
        - price: 价格从低到高
        - -price: 价格从高到低
        - newest: 最新上架（按创建时间倒序）
        - -sales_count: 销量优先（按销量倒序）
        未匹配的排序值默认使用 newest（最新优先）。
        """
        sort_map = {
            'price': 'price',
            '-price': '-price',
            'newest': '-created_at',
            '-sales_count': '-sales_count',
        }
        ordering = sort_map.get(value, '-created_at')
        return queryset.order_by(ordering)

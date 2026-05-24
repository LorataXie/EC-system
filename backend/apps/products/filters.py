import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_keyword')
    category = django_filters.UUIDFilter(field_name='category_id', lookup_expr='exact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    sort = django_filters.CharFilter(method='filter_sort')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price']

    def filter_keyword(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    def filter_sort(self, queryset, name, value):
        sort_map = {
            'price': 'price',
            '-price': '-price',
            'newest': '-created_at',
            '-sales_count': '-sales_count',
        }
        ordering = sort_map.get(value, '-created_at')
        return queryset.order_by(ordering)

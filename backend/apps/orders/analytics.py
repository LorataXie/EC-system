from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from apps.products.models import Product
from django.contrib.auth import get_user_model


def get_dashboard_kpis():
    """仪表盘 KPI 数据"""
    User = get_user_model()

    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = Order.objects.count()
    user_count = User.objects.count()
    product_count = Product.objects.count()

    return {
        'revenue': f'¥{total_revenue:,.0f}',
        'orders': order_count,
        'users': user_count,
        'products': product_count,
    }


def get_sales_trend(months=6):
    """销售趋势（按月）"""
    cutoff = timezone.now() - timedelta(days=months * 30)
    trend = (
        Order.objects.filter(created_at__gte=cutoff)
        .annotate(period=TruncMonth('created_at'))
        .values('period')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('period')
    )
    return [{'period': str(t['period'])[:10], 'total': float(t['total']), 'count': t['count']} for t in trend]


def get_recent_orders(limit=10):
    """最近订单"""
    from .serializers import OrderListSerializer
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')[:limit]
    return OrderListSerializer(orders, many=True).data


def get_hot_products(limit=10):
    """热销商品（按订单中出现的次数排序）"""
    hot = (
        OrderItem.objects.values('product__name', 'product__id')
        .annotate(total_quantity=Sum('quantity'), order_count=Count('order', distinct=True))
        .order_by('-total_quantity')[:limit]
    )
    return [
        {
            'name': h['product__name'],
            'product_id': h['product__id'],
            'total_quantity': h['total_quantity'],
            'order_count': h['order_count'],
        }
        for h in hot
    ]

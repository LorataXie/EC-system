from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from apps.products.models import Product
from django.contrib.auth import get_user_model


def get_dashboard_kpis():
    """
    获取仪表盘核心 KPI 指标数据。

    返回后台管理仪表盘首页的四个关键指标：
    - revenue: 总营收（所有订单总金额之和，格式化为人民币格式）
    - orders: 订单总数
    - users: 注册用户总数
    - products: 商品总数

    这些数据用于后台首页的数据概览卡片展示，
    让管理员一目了然地了解平台的经营概况。
    """
    User = get_user_model()

    # 使用聚合查询一次性获取总营收，避免遍历所有订单
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    # 订单总数
    order_count = Order.objects.count()
    # 注册用户总数
    user_count = User.objects.count()
    # 商品总数
    product_count = Product.objects.count()

    return {
        # 格式化为带有千分位分隔符的人民币格式，如 ¥123,456
        'revenue': f'¥{total_revenue:,.0f}',
        'orders': order_count,
        'users': user_count,
        'products': product_count,
    }


def get_sales_trend(months=6):
    """
    获取销售趋势数据（按月分组）。

    统计最近 N 个月内每个月的销售总额和订单数量，
    用于后台仪表盘绘制销售趋势折线图。

    使用 TruncMonth 将订单按月份截断分组，
    然后通过聚合函数计算每月的总金额和订单数。

    参数:
        months: 统计的月份数（默认6个月）

    返回:
        list[dict]: 每月销售数据列表，每条包含 period（日期）、total（销售额）、count（订单数）
    """
    # 计算截止时间：当前时间向前推 months*30 天
    cutoff = timezone.now() - timedelta(days=months * 30)
    # 按月份分组聚合：统计每月销售额和订单数
    trend = (
        Order.objects.filter(created_at__gte=cutoff)
        .annotate(period=TruncMonth('created_at'))
        .values('period')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('period')
    )
    # 格式化为前端友好的数据结构
    return [{'period': str(t['period'])[:10], 'total': float(t['total']), 'count': t['count']} for t in trend]


def get_recent_orders(limit=10):
    """
    获取最近 N 笔订单。

    按创建时间倒序获取最近的订单列表，
    预加载用户和商品明细信息以优化查询性能。
    使用 OrderListSerializer 序列化，包含订单的所有核心信息。

    参数:
        limit: 返回的订单数量（默认10笔）

    返回:
        list: 序列化后的订单字典列表
    """
    from .serializers import OrderListSerializer
    # 按创建时间倒序获取最近订单，预加载关联数据减少查询
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')[:limit]
    return OrderListSerializer(orders, many=True).data


def get_hot_products(limit=10):
    """
    获取热销商品排行榜。

    从订单明细中按商品分组统计，按总销售数量降序排列。
    统计维度：
    - total_quantity: 该商品在所有订单中的总销售数量
    - order_count: 包含该商品的订单数量（去重）

    注意：这里统计的是订单中的实际销售数据，
    而非 Product.sales_count 字段，因为后者可能被手动修改。

    参数:
        limit: 返回的榜单商品数量（默认前10名）

    返回:
        list[dict]: 热销商品列表，每条包含 name（商品名）、product_id（商品ID）、
                    total_quantity（总销量）、order_count（涉及订单数）
    """
    # 从订单明细中按商品分组聚合，统计总销量和涉及订单数
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

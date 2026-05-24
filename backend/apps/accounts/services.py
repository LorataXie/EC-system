from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from apps.orders.models import Order


def get_consumption_stats(user, period='month', start_date=None, end_date=None):
    orders = Order.objects.filter(user=user)

    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)

    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders.count()

    trunc_fn = {'day': TruncDay, 'week': TruncWeek, 'month': TruncMonth}.get(period, TruncMonth)
    trend = (
        orders.annotate(period=trunc_fn('created_at'))
        .values('period')
        .annotate(total=Sum('total_amount'), count=Count('id'))
        .order_by('period')
    )

    category_data = (
        orders.filter(items__product__category__isnull=False)
        .values('items__product__category__name')
        .annotate(total=Sum('items__price'))
        .order_by('-total')[:10]
    )

    return {
        'total_spent': float(total_spent),
        'order_count': order_count,
        'trend': list(trend),
        'categories': list(category_data),
    }

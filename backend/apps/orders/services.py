from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import Order, OrderItem


def generate_order_no():
    now = datetime.now()
    date_part = now.strftime('%Y%m%d%H%M%S')
    import random
    rand_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f'{date_part}{rand_part}'


def validate_stock(cart_items):
    errors = []
    for item in cart_items:
        product = item.product
        if product.stock == 0:
            errors.append(f'商品 "{product.name}" 已售罄')
        elif item.quantity > product.stock:
            errors.append(f'商品 "{product.name}" 库存不足，剩余 {product.stock}')
    return errors


@transaction.atomic
def create_order(user, selected_items, address_id=None, coupon=None):
    if not selected_items:
        raise ValueError('没有选中商品')

    errors = validate_stock(selected_items)
    if errors:
        raise ValueError('; '.join(errors))

    # Capture address snapshot
    addr_snapshot = {}
    if address_id:
        from apps.accounts.models import Address
        addr = Address.objects.filter(id=address_id, user=user).first()
        if addr:
            addr_snapshot = {
                'recipient_name': addr.recipient_name,
                'phone': addr.phone,
                'country': addr.country,
                'state': addr.state,
                'city': addr.city,
                'address_line1': addr.address_line1,
                'address_line2': addr.address_line2,
                'postal_code': addr.postal_code,
            }

    total_amount = sum(item.quantity * item.product.price for item in selected_items)
    discount_amount = 0.00

    if coupon:
        from apps.coupons.services import CouponValidator, CouponCalculator
        is_eligible, err_msg = CouponValidator.is_eligible(coupon, total_amount)
        if not is_eligible:
            raise ValueError(err_msg)
        discount_amount = CouponCalculator.calculate(coupon, total_amount)
        coupon.status = 'used'
        coupon.save(update_fields=['status'])

    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        discount_amount=discount_amount,
        coupon=coupon,
        address_snapshot=addr_snapshot,
    )

    for item in selected_items:
        product = item.product
        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,
            quantity=item.quantity,
        )
        product.stock -= item.quantity
        product.sales_count += item.quantity
        product.save(update_fields=['stock', 'sales_count'])

    selected_items.delete()
    return order


def cancel_expired_orders(minutes=30):
    """取消超过指定分钟数的待支付订单，恢复库存"""
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(minutes=minutes)
    expired = Order.objects.filter(status='pending', created_at__lt=cutoff)
    count = 0
    for order in expired:
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        count += 1
    return count

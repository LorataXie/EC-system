from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import Order, OrderItem


def generate_order_no():
    """
    生成唯一的订单编号。

    格式：YYYYMMDDHHmmss + 4位随机数字
    例如：20260525143022 + 7831

    使用时间戳 + 随机数的方式生成订单号，兼顾可读性和唯一性。
    在生产环境中可能使用雪花算法（Snowflake）或 Redis 自增 ID 确保
    高并发场景下的唯一性。
    """
    now = datetime.now()
    date_part = now.strftime('%Y%m%d%H%M%S')
    import random
    rand_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f'{date_part}{rand_part}'


def validate_stock(cart_items):
    """
    校验收货商品库存是否充足。

    遍历选中的购物车条目，检查每个商品：
    - 库存为 0：提示"已售罄"
    - 购买数量超过库存：提示"库存不足"，并告知剩余库存

    参数:
        cart_items: 选中的购物车条目 QuerySet

    返回:
        list[str]: 错误信息列表，空列表表示库存校验通过
    """
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
    """
    创建订单（数据库事务保护）。

    在单个数据库事务中原子性地完成以下操作：
    1. 校验购物车条目是否为空
    2. 校验所有商品库存是否充足
    3. 生成收货地址快照（JSON 格式保存，避免地址被修改后影响历史订单）
    4. 计算订单总金额
    5. 如果使用优惠券，校验优惠券是否可用并计算抵扣金额
    6. 创建订单主记录（Order）
    7. 创建所有订单明细记录（OrderItem），快照商品价格
    8. 扣减商品库存（防止超卖）
    9. 更新商品销量（用于热销排行）
    10. 删除已下单的购物车条目（清空购物车中已购买的商品）

    任何一步失败都会回滚整个事务，确保数据一致性。

    参数:
        user: 下单用户
        selected_items: 选中的购物车条目 QuerySet（已 select_related('product')）
        address_id: 收货地址 ID（可选）
        coupon: 优惠券对象（可选）

    返回:
        Order: 创建成功的订单对象

    异常:
        ValueError: 校验失败时抛出，包含具体的错误描述
    """
    if not selected_items:
        raise ValueError('没有选中商品')

    # 库存校验
    errors = validate_stock(selected_items)
    if errors:
        raise ValueError('; '.join(errors))

    # Capture address snapshot
    # 生成收货地址快照：将地址的完整信息以 JSON 格式保存到订单中
    # 这样即使用户后期修改或删除地址，订单中的历史地址信息也不会丢失
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

    # 计算订单总金额（优惠前，商品原价总和）
    total_amount = sum(item.quantity * item.product.price for item in selected_items)
    discount_amount = 0.00

    # 处理优惠券：校验可用性并计算抵扣金额
    if coupon:
        from apps.coupons.services import CouponValidator, CouponCalculator
        # 校验优惠券是否满足使用条件（如最低消费金额）
        is_eligible, err_msg = CouponValidator.is_eligible(coupon, total_amount)
        if not is_eligible:
            raise ValueError(err_msg)
        # 计算优惠券抵扣金额
        discount_amount = CouponCalculator.calculate(coupon, total_amount)
        # 优惠券标记为已使用（防止重复使用）
        coupon.status = 'used'
        coupon.save(update_fields=['status'])

    # 创建订单主记录
    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        discount_amount=discount_amount,
        coupon=coupon,
        address_snapshot=addr_snapshot,
    )

    # 创建订单明细并更新商品库存和销量
    for item in selected_items:
        product = item.product
        # 创建订单明细，快照下单时价格
        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,
            quantity=item.quantity,
        )
        # 扣减库存（防止超卖）
        product.stock -= item.quantity
        # 增加销量（用于热销排行）
        product.sales_count += item.quantity
        product.save(update_fields=['stock', 'sales_count'])

    # 下单成功后删除购物车中已购买的商品条目
    selected_items.delete()
    return order


def cancel_expired_orders(minutes=30):
    """
    取消超过指定分钟数的待支付订单，恢复库存。

    查找所有 status 为 pending 且创建时间早于 cutoff 的订单，
    将其状态改为 cancelled，同时恢复所有订单明细中商品的库存。
    用于清理超时未支付的僵尸订单，释放被锁定的库存资源。

    参数:
        minutes: 超时分钟数（默认30分钟），超过此时间的待支付订单将被取消

    返回:
        int: 被取消的订单数量
    """
    from datetime import timedelta
    cutoff = timezone.now() - timedelta(minutes=minutes)
    expired = Order.objects.filter(status='pending', created_at__lt=cutoff)
    count = 0
    for order in expired:
        # 恢复每个订单明细的商品库存
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save(update_fields=['stock'])
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        count += 1
    return count

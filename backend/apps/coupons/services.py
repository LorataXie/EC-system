from django.utils import timezone
from decimal import Decimal
from .models import Coupon


class CouponValidator:
    @staticmethod
    def is_eligible(coupon, order_total):
        if coupon.status != 'unused':
            return False, '优惠券已使用或已过期'
        now = timezone.now()
        if now < coupon.start_time or now > coupon.end_time:
            if now > coupon.end_time and coupon.status == 'unused':
                coupon.status = 'expired'
                coupon.save(update_fields=['status'])
            return False, '优惠券不在有效期内'
        if order_total < coupon.min_order_amount:
            return False, f'订单金额未达到最低使用金额 ¥{coupon.min_order_amount}'
        return True, ''


class CouponCalculator:
    @staticmethod
    def calculate(coupon, order_total):
        if coupon.type == 'full_reduction':
            return min(Decimal(str(coupon.discount_value)), order_total)
        elif coupon.type == 'discount':
            discount = order_total * (Decimal(str(coupon.discount_value)) / Decimal('100'))
            return min(discount, order_total)
        elif coupon.type == 'fixed_amount':
            return min(Decimal(str(coupon.discount_value)), order_total)
        return Decimal('0.00')


class CouponDistributor:
    @staticmethod
    def create_coupons(
        type,
        discount_value,
        min_order_amount,
        start_time,
        end_time,
        status='unused',
        count=1,
    ):
        coupons = []
        for _ in range(count):
            coupon = Coupon.objects.create(
                type=type,
                discount_value=discount_value,
                min_order_amount=min_order_amount,
                start_time=start_time,
                end_time=end_time,
                status=status,
            )
            coupons.append(coupon)
        return coupons

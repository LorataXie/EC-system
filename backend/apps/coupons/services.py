"""
优惠券模块 - 服务层 (services)

将核心业务逻辑从视图中抽离，遵循"瘦视图、肥服务"的设计原则:
- 视图层负责 HTTP 协议相关 (请求解析、响应构造、权限校验)
- 服务层负责纯业务逻辑 (与 HTTP 无关)，可跨视图复用，便于单元测试

包含三个服务类:
1. CouponValidator:   优惠券使用资格校验
2. CouponCalculator:  优惠金额计算 (支持多种优惠类型)
3. CouponDistributor: 优惠券批量创建工具
"""

from django.utils import timezone
from decimal import Decimal
from .models import Coupon


class CouponValidator:
    """
    优惠券使用资格校验器

    负责验证一张优惠券是否可以被用户在指定订单上使用。
    校验维度:
    1. 券状态是否为 'unused' (未使用)
    2. 当前时间是否在券的有效期内
    3. 订单金额是否满足最低消费门槛

    为何使用静态方法: 校验逻辑无状态，不依赖实例变量，静态方法更轻量。
    为何放在服务层而非模型中: 校验逻辑涉及时间判断和状态变更，
    放在服务层便于 mock 和单元测试。
    """

    @staticmethod
    def is_eligible(coupon, order_total):
        """
        检查优惠券是否可用

        Args:
            coupon:      要校验的 Coupon 实例
            order_total: 订单总金额 (Decimal)

        Returns:
            (is_eligible: bool, reason: str)
            - (True, ''):    可以使用
            - (False, msg):  不可使用，msg 为具体原因 (用于前端提示)
        """
        # ----- 校验1: 券状态 -----
        # 只有 'unused' 状态的券才能使用，已使用或已过期的券直接拒绝
        if coupon.status != 'unused':
            return False, '优惠券已使用或已过期'

        # ----- 校验2: 有效期 -----
        now = timezone.now()
        if now < coupon.start_time or now > coupon.end_time:
            # 懒过期策略: 如果当前时间已超过 end_time 且券仍为 'unused'，
            # 则顺便将券标记为 'expired'，下次校验时直接被校验1拦截
            # 这样设计是为了避免依赖定时任务来批量更新过期状态
            if now > coupon.end_time and coupon.status == 'unused':
                coupon.status = 'expired'
                coupon.save(update_fields=['status'])  # update_fields 只更新 status 字段，减少数据库写入量
            return False, '优惠券不在有效期内'

        # ----- 校验3: 最低消费门槛 -----
        # 订单总价必须 >= 券的 min_order_amount 才能使用
        # 例如: 满100减20 → 订单金额必须 >= 100 元
        if order_total < coupon.min_order_amount:
            return False, f'订单金额未达到最低使用金额 ¥{coupon.min_order_amount}'

        # 所有校验通过
        return True, ''


class CouponCalculator:
    """
    优惠金额计算器

    负责根据优惠券类型计算实际减免金额。
    支持三种优惠类型:
    - full_reduction: 满减 (如满100减20 → 减免20元)
    - discount:       折扣 (如8折 → 减免 order_total * 20%)
    - fixed_amount:   固定金额 (如直接减免15元)
                      (discount 和 fixed_amount 为预留扩展类型，当前 COUPON_TYPES 仅包含 full_reduction)

    为何使用 staticmethod: 计算逻辑无状态，纯函数式，便于测试。
    为何对 Decimal 使用 str() 包装: 避免 Decimal 从 float 构造时的精度丢失问题，
    如 Decimal(0.1) 会产生 Decimal('0.1000000000000000055511151231257827021181583404541015625')，
    而 Decimal(str(0.1)) 才是精确的 Decimal('0.1')。
    """

    @staticmethod
    def calculate(coupon, order_total):
        """
        计算优惠券实际减免金额

        Args:
            coupon:     使用的优惠券实例
            order_total: 订单原始总金额

        Returns:
            Decimal: 实际减免金额，不会超过订单总金额
        """
        if coupon.type == 'full_reduction':
            # 满减: 直接减去 discount_value，但不能减到负数
            # 例: 订单100元，满减券20元 → 减免20元
            return min(Decimal(str(coupon.discount_value)), order_total)

        elif coupon.type == 'discount':
            # 折扣: discount_value 代表折扣百分比，如 80 表示打8折 (即减免20%)
            # 计算方式: order_total * (discount_value / 100)
            discount = order_total * (Decimal(str(coupon.discount_value)) / Decimal('100'))
            return min(discount, order_total)

        elif coupon.type == 'fixed_amount':
            # 固定金额: 同满减逻辑，直接减去固定值
            return min(Decimal(str(coupon.discount_value)), order_total)

        # 未知类型 → 不减免 (安全兜底)
        return Decimal('0.00')


class CouponDistributor:
    """
    优惠券批量创建工具

    用于程序化批量生成优惠券 (如注册送券、活动赠券等场景)。
    与 CouponAdminViewSet.issue 的区别:
    - issue 是面向 HTTP 请求的管理员批量发放接口
    - CouponDistributor 是面向内部代码的服务层工具，可被任务队列、信号等其他模块调用

    注意: 此方法创建的优惠券不绑定用户 (user=None)，
    适合预生成券池后再分配给用户。
    """

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
        """
        批量创建优惠券

        Args:
            type:              优惠券类型 (如 'full_reduction')
            discount_value:    折扣值/金额
            min_order_amount:  最低订单金额
            start_time:        生效时间
            end_time:          失效时间
            status:            初始状态，默认 'unused'
            count:             创建张数，默认 1

        Returns:
            list[Coupon]: 创建的优惠券列表
        """
        coupons = []
        for _ in range(count):
            coupon = Coupon.objects.create(
                type=type,
                discount_value=discount_value,
                min_order_amount=min_order_amount,
                start_time=start_time,
                end_time=end_time,
                status=status,
                # 注意: 此处不传 user，券处于未分配状态
            )
            coupons.append(coupon)
        return coupons

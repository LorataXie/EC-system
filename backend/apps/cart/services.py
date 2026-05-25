from .models import Cart


def get_or_create_cart(user):
    """
    获取或创建用户的购物车（懒加载模式）。

    每个用户只有唯一一个购物车。用户首次访问购物车相关功能时
    自动创建购物车记录，后续操作复用已有的购物车。
    这种设计避免了在用户注册时就创建购物车的冗余操作。

    参数:
        user: 当前登录用户对象

    返回:
        Cart: 用户对应的购物车实例
    """
    # get_or_create 保证原子性：并发场景下不会创建重复购物车
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

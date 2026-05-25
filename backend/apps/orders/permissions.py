from rest_framework.permissions import BasePermission


class IsOrderOwnerOrAdmin(BasePermission):
    """
    订单所有者或管理员权限类。

    用于对象级别的权限控制，确保：
    - 管理员（is_staff=True）可以访问任意订单
    - 普通用户只能访问自己的订单

    使用场景：
    - 订单详情、取消、支付等操作需要验证操作者是否为订单所有者或管理员
    - 在每个需要对象级权限的 action 中通过 self.check_object_permissions 调用

    这种设计保证了用户之间的订单隔离，同时允许管理员具备管理所有订单的能力。
    """
    def has_object_permission(self, request, view, obj):
        """
        检查当前用户是否有权限访问指定的订单对象。

        参数:
            request: HTTP 请求对象
            view: 当前视图
            obj: 要检查权限的订单对象

        返回:
            bool: True 表示有权限，False 表示无权限
        """
        # 管理员拥有所有订单的访问权限
        if request.user and request.user.is_staff:
            return True
        # 普通用户只能访问自己的订单
        return obj.user == request.user

"""
核心模块 - 权限控制

定义项目中复用的自定义 DRF 权限类。
DRF 的权限机制在视图处理请求之前运行，用于决定是否允许请求继续执行。
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    """
    管理员权限：仅允许 staff 用户访问。

    使用场景：后台管理接口，如用户管理、数据统计等。
    检查逻辑：用户必须已认证 且 is_staff 为 True。
    """

    def has_permission(self, request, view):
        """
        视图级权限检查，在调用视图的任何方法之前执行。
        只有已登录且 is_staff=True 的用户才能通过。

        Args:
            request: DRF 的 Request 对象，包含当前用户信息
            view: 被访问的视图对象

        Returns:
            bool: True 表示允许访问，False 表示拒绝（返回 403）
        """
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    资源所有者或管理员权限：允许资源的所有者或管理员操作。

    与 IsAdminUser 的区别：这个是对象级权限，在 has_permission 通过后，
    针对具体对象进行二次检查。普通用户可以操作自己的资源，管理员可以操作所有资源。

    使用场景：用户修改自己的收货地址、订单等，同时允许管理员代为管理。
    """

    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查，在视图获取具体对象后执行（如 retrieve/update/destroy）。

        Args:
            request: DRF 的 Request 对象
            view: 被访问的视图对象
            obj: 将要被操作的具体模型实例

        Returns:
            bool: 管理员可直接通过；普通用户仅当 obj.user == request.user 时通过
        """
        # 管理员拥有所有权限，直接放行
        if request.user and request.user.is_staff:
            return True
        # 检查对象是否有 user 外键，且当前用户是该对象的所有者
        return hasattr(obj, 'user') and obj.user == request.user

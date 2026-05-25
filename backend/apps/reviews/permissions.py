"""
商品评价模块 - 权限类 (permissions)

该文件用于存放评价模块的自定义权限类。

当前为空文件，作为权限扩展的预留位置。

未来可能添加的权限类:
- CanReviewProduct:  验证用户是否购买过该商品 (防止未购买者评价)
- CanUploadImage:    验证用户是否有权限上传评价图片 (如防止滥用)
- ReviewThrottle:    评价频率限制 (防止刷评价)

当前评价相关的权限控制已通过以下方式实现:
- apps/core/permissions.py 中的 IsOwnerOrAdmin (评价者可编辑自己的评价)
- ReviewViewSet 中的 perform_create (订单状态校验)
"""
# 当前无自定义权限类，依赖 apps.core.permissions 中的通用权限类

"""
核心模块 - 基础数据模型

提供项目中所有模型的公共基类，包含 UUID 主键和时间戳字段，
避免在每个应用中重复定义相同的基础字段。
"""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    抽象基类模型，为所有业务模型提供统一的公共字段。

    使用 UUID 作为主键而非自增 ID 的原因：
    1. 分布式环境下避免主键冲突
    2. 对外暴露时不会泄露数据量（自增ID可被遍历）
    3. 前后端分离时前端可提前生成 ID，减少网络往返

    包含自动管理的时间戳：
    - created_at: 记录创建时间，用于排序和审计
    - updated_at: 记录最后更新时间，用于数据变更追踪
    """

    # UUID 主键：使用 uuid4 生成全局唯一标识符，不可编辑，防止人为篡改
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 创建时间：auto_now_add=True 表示仅在对象首次创建时自动设置
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    # 更新时间：auto_now=True 表示每次调用 save() 时自动更新为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # abstract=True 表示这是抽象基类，不会在数据库中创建独立的表
        # 子类继承后会拥有这些字段，但字段存储在子类自己的表中
        abstract = True

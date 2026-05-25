"""
商品评价模块 - Django 信号 (signals)

使用 Django 的信号机制实现评分统计的自动维护。

核心逻辑:
当评价被创建(post_save)或删除(post_delete)时，自动重新计算该商品的平均评分，
并更新 Product 模型的 rating_avg 字段。

为何使用信号而非在视图中手动更新:
1. 解耦: 评分更新逻辑与视图逻辑分离，任何方式创建/删除评价 (API、Admin、脚本)
   都会触发信号自动更新评分
2. 一致性: 避免在多个地方重复写评分更新代码
3. 可靠性: 信号在事务内执行，保证数据一致性

注意事项:
- post_save 在每次 save() 调用后触发，包括评价的创建和更新
- 使用 update_fields=['rating_avg'] 只更新评分字段，避免覆盖商品的其他字段
"""

from django.db.models import Avg  # Django ORM 的聚合函数，计算平均值
from django.db.models.signals import post_save, post_delete  # 模型保存后、删除后信号
from django.dispatch import receiver  # 信号接收器装饰器
from .models import Review


# =========================================================================
# 信号接收器: 评价变更时自动更新商品平均评分
#
# @receiver 装饰器的作用:
# 1. 将 update_product_rating 函数注册为信号接收器
# 2. 参数 sender=Review 表示只监听 Review 模型的信号
# 3. 同时监听 post_save 和 post_delete 两个信号类型
#
# 触发场景:
# - 用户创建新评价 → post_save 触发 → 新增评分纳入平均值计算
# - 用户修改评价评分 → post_save 触发 → 更新分值重新计算
# - 管理员删除评价 → post_delete 触发 → 移除评分后重新计算
# =========================================================================
@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """
    当评价被创建、更新或删除时，自动重新计算并更新对应商品的平均评分

    Args:
        sender:   发送信号的模型类 (此处为 Review)
        instance: 被保存/删除的 Review 实例
        **kwargs: 额外参数 (如 created, update_fields 等)

    计算过程:
    1. 获取该评价关联的商品对象 (instance.product)
    2. 聚合查询该商品的所有评价的平均评分
    3. 四舍五入保留两位小数
    4. 更新 product.rating_avg 字段
    5. 使用 update_fields=['rating_avg'] 只保存评分字段，避免不必要的全字段更新
       (同时也避免了 save() 递归触发其他信号)
    """
    # 第一步: 获取评价关联的商品
    product = instance.product

    # 第二步: 使用 Django ORM 的 aggregate 计算该商品所有评价的平均评分
    # filter(product=product): 只计算该商品的评价
    # Avg('rating'): 对 rating 字段求平均值
    # 返回格式: {'a': 4.5} 或 {'a': None} (无评价时)
    avg = Review.objects.filter(product=product).aggregate(a=Avg('rating'))['a']

    # 第三步: 格式化平均值
    # - 如果有评价 → round(float(avg), 2) 保留两位小数
    # - 如果没有评价 (avg 为 None) → 设为 0.00
    # 使用 float 转换: Decimal/None → float → round，确保得到 Python 原生 float
    product.rating_avg = round(float(avg), 2) if avg else 0.00

    # 第四步: 只更新 rating_avg 字段，避免全字段 save
    # update_fields=['rating_avg'] 的好处:
    # 1. 性能: 只更新一个字段，SQL UPDATE 语句更短
    # 2. 安全: 不会覆盖其他字段的并发修改
    # 3. 避免递归: 不会触发其他字段的 save 信号
    product.save(update_fields=['rating_avg'])

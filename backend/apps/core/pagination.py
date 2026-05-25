"""
核心模块 - 分页配置

提供全局统一的分页工具，所有列表接口共享相同的分页参数和默认值，
确保前端调用不同接口时分页行为一致。
"""
from rest_framework.pagination import PageNumberPagination


# 全局统一分页工具配置
class StandardPageNumberPagination(PageNumberPagination):
    """
    标准分页器，基于页码的分页方式。

    为什么选择基于页码的分页（而非游标分页）：
    1. 电商场景下用户需要跳转到特定页码（如第3页商品列表）
    2. 后端管理界面需要直观的翻页控件
    3. 实现简单，前端对接方便

    配置说明：
    - page_size: 默认每页 20 条，平衡了加载速度和信息密度
    - page_size_query_param: 允许前端通过 ?page_size=50 动态调整每页数量
    - max_page_size: 防止前端请求过大页面导致性能问题，上限 100 条
    """

    # 默认每页返回 20 条记录
    page_size = 20

    # 前端可通过 URL 参数 page_size 自行指定每页条数
    page_size_query_param = 'page_size'

    # 限制前端最大可请求的每页条数，防止一次性拉取过多数据拖垮数据库
    max_page_size = 100

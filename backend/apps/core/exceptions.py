"""
核心模块 - 全局异常处理

将 DRF 未捕获的异常统一转换为标准的 {code, message, data} 响应格式。
与 CustomJSONRenderer 配合使用，确保成功和失败响应都使用相同的三层结构，
前端只需处理一种响应格式。

默认情况下 DRF 的异常响应格式是 {detail: ..., ...}，经过此处理器后
会变成 {code: 400, message: 'error', data: {detail: ..., ...}}，
与正常响应格式保持统一。
"""
from rest_framework.views import exception_handler


# 全局错误格式化工具
def custom_exception_handler(exc, context):
    """
    自定义 DRF 异常处理器，将异常响应重新格式化为统一结构。

    Args:
        exc: 抛出的异常对象（如 ValidationError, NotAuthenticated 等）
        context: DRF 传递的上下文，包含 view 和 request 等信息

    Returns:
        Response 或 None: 格式化后的响应对象；若异常无法处理则返回 None

    工作原理：
    1. 先调用 DRF 默认的异常处理器，获取标准异常响应
    2. 如果响应存在，将其原始 data 作为新格式的 data 字段
    3. 保留原始 HTTP 状态码，将 message 设为 'error'
    """
    # 调用 DRF 内置的异常处理器，获得标准格式的异常响应
    response = exception_handler(exc, context)

    # 如果 DRF 成功处理了该异常（返回了 Response 对象）
    if response is not None:
        # 保存原始的异常数据（如 {'detail': '未认证'} 或字段校验错误等）
        errors = response.data
        # 重新组装为标准的三层结构：{code, message, data}
        response.data = {
            'code': response.status_code,
            'message': 'error',
            'data': errors  # 原始错误详情放在 data 中，前端可从中读取具体错误原因
        }

    return response

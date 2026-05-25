"""
核心模块 - 自定义 JSON 渲染器

统一所有 API 接口的响应格式，确保前端收到的数据始终包含 {code, message, data} 三层结构。
这样做的好处：
1. 前端可以用统一的拦截器处理业务状态码，无需为每个接口写不同的解析逻辑
2. 错误信息和成功数据使用相同的包裹层，降低前后端沟通成本
3. 分页数据等 DRF 内置响应也能被正确包裹
"""
from rest_framework.renderers import JSONRenderer


# 全局统一接口返回格式化工具
class CustomJSONRenderer(JSONRenderer):
    """
    自定义 JSON 渲染器，在 DRF 返回原始数据前将其包裹进统一的响应结构。

    响应结构：
    {
        "code": 200,           // HTTP 状态码，前端可据此判断请求是否成功
        "message": "success",  // 提示信息，成功时为 "success"，失败时为具体错误描述
        "data": { ... }        // 实际业务数据，可以是对象、数组或 null
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        重写 DRF JSONRenderer 的 render 方法，拦截并格式化响应数据。

        Args:
            data: 视图返回的原始数据（字典、列表或 None）
            accepted_media_type: 客户端接受的媒体类型
            renderer_context: DRF 传递的渲染上下文，包含 response 对象

        Returns:
            bytes: JSON 序列化后的字节串
        """
        # 获取当前请求的响应对象，用于读取 HTTP 状态码
        response = renderer_context.get('response')
        status_code = response.status_code if response else 200

        # 情况1：data 为 None（如删除操作），返回空数据体
        if data is None:
            return super().render(
                {'code': status_code, 'message': 'success', 'data': None},
                accepted_media_type, renderer_context
            )

        # 情况2：data 已经包含 code 和 message 字段（如分页响应），不做二次包裹
        if 'code' in data and 'message' in data:
            return super().render(data, accepted_media_type, renderer_context)

        # 情况3：普通业务数据，包裹进统一结构
        return super().render(
            {'code': status_code, 'message': 'success', 'data': data},
            accepted_media_type, renderer_context
        )

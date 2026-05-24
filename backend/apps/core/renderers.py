from rest_framework.renderers import JSONRenderer

#全局统一接口返回格式化工具
class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        status_code = response.status_code if response else 200

        if data is None:
            return super().render(
                {'code': status_code, 'message': 'success', 'data': None},
                accepted_media_type, renderer_context
            )

        if 'code' in data and 'message' in data:
            return super().render(data, accepted_media_type, renderer_context)

        return super().render(
            {'code': status_code, 'message': 'success', 'data': data},
            accepted_media_type, renderer_context
        )

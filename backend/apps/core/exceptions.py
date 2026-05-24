from rest_framework.views import exception_handler
#全局错误格式化工具

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        response.data = {
            'code': response.status_code,
            'message': 'error',
            'data': errors
        }

    return response

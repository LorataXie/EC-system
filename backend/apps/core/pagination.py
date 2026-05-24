from rest_framework.pagination import PageNumberPagination

#全局统一分页工具配置
class StandardPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

from rest_framework import pagination
from rest_framework.response import Response

from core.common.exception.api_response import ApiResponse


class StandardPagination(pagination.PageNumberPagination):
    """
    标准分页器
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return ApiResponse.ok(content={
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


def paginated_response(request, queryset, serializer_class, page_size=10):
    """
    通用分页响应函数
    """
    paginator = StandardPagination()
    paginator.page_size = request.query_params.get('page_size', page_size)
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

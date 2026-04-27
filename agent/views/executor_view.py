"""执行器管理 ViewSet"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from agent.models import ElExecutor
from agent.serializers import ExecutorSerializer
from agent.schemas import get_all_executor_schemas
from core.common.exception.api_response import ApiResponse


class ExecutorViewSet(viewsets.ModelViewSet):
    """执行器管理。

    - list/retrieve: 只读查看
    - update: 修改 enabled 和 metadata
    - create/destroy: 禁用（执行器通过管理命令注册）
    - types action: 返回所有执行器的 schema 定义
    """

    permission_classes = [IsAuthenticated]
    queryset = ElExecutor.objects.all().order_by("created_at")
    serializer_class = ExecutorSerializer

    def create(self, request, *args, **kwargs):
        return ApiResponse.error(
            message="执行器通过管理命令注册，不可手动创建",
            http_status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return ApiResponse.error(
            message="执行器不可删除",
            http_status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.ok(content=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.ok(content=serializer.data)

    @action(detail=False, methods=["get"], url_path="types")
    def types(self, request):
        """返回所有执行器的 schema 定义。"""
        return ApiResponse.ok(content=get_all_executor_schemas())

from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_response import ApiResponse
from core.common.pagination import StandardPagination
from llm.models import ElLLMProvider, ElLLMModel
from llm.serializers import (
    ElLLMProviderSerializer,
    ElLLMProviderCreateSerializer,
    ElLLMModelSerializer,
    ElLLMModelDropdownSerializer,
)
from llm.filters import ElLLMProviderFilter, ElLLMModelFilter


def _is_admin(request):
    return request.user.is_authenticated and request.user.is_superuser


class ElLLMProviderViewSet(viewsets.ModelViewSet):
    """LLM 供应商管理"""

    permission_classes = [IsAuthenticated]
    queryset = ElLLMProvider.objects.all().order_by("-created_at")
    filterset_class = ElLLMProviderFilter
    search_fields = ["code", "name"]
    ordering_fields = ["created_at", "updated_at"]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ElLLMProviderCreateSerializer
        return ElLLMProviderSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def create(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.ok(
            content=serializer.data, http_status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.ok(content=serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return ApiResponse(
                message=f"供应商「{instance.name}」已被 Agent 关联，无法删除。",
                http_status=status.HTTP_409_CONFLICT,
            )
        return ApiResponse.ok(message="删除成功")


class ElLLMModelViewSet(viewsets.ModelViewSet):
    """LLM 模型管理"""

    permission_classes = [IsAuthenticated]
    queryset = ElLLMModel.objects.select_related("provider").all().order_by("sort_order", "id")
    filterset_class = ElLLMModelFilter
    search_fields = ["model_code", "display_name"]
    ordering_fields = ["sort_order", "created_at"]
    pagination_class = StandardPagination

    serializer_class = ElLLMModelSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def create(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.ok(
            content=serializer.data, http_status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.ok(content=serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not _is_admin(request):
            return ApiResponse(
                message="需要管理员权限",
                http_status=status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return ApiResponse(
                message=f"模型「{instance.display_name}」已被 Agent 关联，无法删除。",
                http_status=status.HTTP_409_CONFLICT,
            )
        return ApiResponse.ok(message="删除成功")

    @action(detail=False, methods=["get"])
    def dropdown(self, request):
        """下拉选项接口"""
        models = (
            ElLLMModel.objects.select_related("provider")
            .filter(enabled=True)
            .order_by("sort_order", "id")
        )
        serializer = ElLLMModelDropdownSerializer(models, many=True)
        return ApiResponse.ok(content=serializer.data)

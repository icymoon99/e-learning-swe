from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_response import ApiResponse
from core.common.pagination import StandardPagination
from git_source.models import ElGitSource
from git_source.serializers import (
    GitSourceSerializer,
    GitSourceCreateUpdateSerializer,
    GitSourceDropdownSerializer,
)
from git_source.filters import ElGitSourceFilter


def _is_admin(request):
    """检查是否为管理员"""
    return request.user.is_authenticated and request.user.is_superuser


class GitSourceViewSet(viewsets.ModelViewSet):
    """仓库源管理"""

    permission_classes = [IsAuthenticated]
    queryset = ElGitSource.objects.all().order_by("-created_at")
    filterset_class = ElGitSourceFilter
    search_fields = ["name", "repo_url"]
    ordering_fields = ["created_at", "updated_at"]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return GitSourceCreateUpdateSerializer
        return GitSourceSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
        self.perform_destroy(instance)
        return ApiResponse.ok(message="删除成功")

    @action(detail=False, methods=["get"])
    def dropdown(self, request):
        """下拉选项接口（不返回 token）"""
        sources = ElGitSource.objects.all().order_by("name")
        serializer = GitSourceDropdownSerializer(sources, many=True)
        return ApiResponse.ok(content=serializer.data)

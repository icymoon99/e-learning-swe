from django.db.models import ProtectedError
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
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return ApiResponse(
                message=f"仓库源「{instance.name}」已被任务关联，无法删除。请先删除或解绑相关任务后再试。",
                http_status=status.HTTP_409_CONFLICT,
            )
        return ApiResponse.ok(message="删除成功")

    @action(detail=False, methods=["get"])
    def dropdown(self, request):
        """下拉选项接口（不返回 token）"""
        sources = ElGitSource.objects.all().order_by("name")
        serializer = GitSourceDropdownSerializer(sources, many=True)
        return ApiResponse.ok(content=serializer.data)

    @action(detail=False, methods=["get"])
    def repos(self, request):
        """获取远程仓库列表（根据 Token 查询）"""
        platform = request.query_params.get("platform")
        token = request.query_params.get("token")
        api_url = request.query_params.get("api_url")

        if not platform or not token:
            return ApiResponse.parameter_error(message="platform 和 token 为必填参数")

        from git_source.services.platform_api import list_remote_repos
        try:
            repos = list_remote_repos(platform, token, api_url)
        except Exception as e:
            return ApiResponse.error(message=f"获取仓库列表失败: {e}")

        return ApiResponse.ok(content={"repos": repos})

    @action(detail=False, methods=["get"])
    def branches(self, request):
        """获取指定仓库的分支列表（根据 Token 查询）"""
        source_id = request.query_params.get("source_id")
        platform = request.query_params.get("platform")
        token = request.query_params.get("token")
        repo_full_name = request.query_params.get("repo_full_name")
        api_url = request.query_params.get("api_url")

        # 如果传了 source_id，从数据库获取平台、token 和仓库信息
        if source_id:
            from git_source.models import ElGitSource
            try:
                source = ElGitSource.objects.get(id=source_id)
                platform = source.platform
                token = source.token
                # 从 repo_url 中提取 repo_full_name
                # 支持 https://github.com/owner/repo 和 git@github.com:owner/repo.git 格式
                repo_url = source.repo_url.rstrip("/")
                repo_full_name = repo_url.rsplit("/", 2)[-2] + "/" + repo_url.rsplit("/", 1)[-1].removesuffix(".git")
            except ElGitSource.DoesNotExist:
                return ApiResponse.error(message="仓库源不存在")

        if not platform or not token or not repo_full_name:
            return ApiResponse.parameter_error(message="platform、token 和 repo_full_name 为必填参数，或提供 source_id")

        from git_source.services.platform_api import list_branches
        try:
            result = list_branches(platform, token, repo_full_name, api_url)
        except Exception as e:
            return ApiResponse.error(message=f"获取分支列表失败: {e}")

        return ApiResponse.ok(content=result)

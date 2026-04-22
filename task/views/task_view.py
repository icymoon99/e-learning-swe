from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import StandardPagination
from task.models import ElTask, ElTaskConversation
from task.serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
)
from task.filters import ElTaskFilter


def _is_admin(request):
    return request.user.is_authenticated and request.user.is_superuser


class TaskViewSet(viewsets.ModelViewSet):
    """任务管理"""

    permission_classes = [IsAuthenticated]
    filterset_class = ElTaskFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]
    pagination_class = StandardPagination

    def get_queryset(self):
        return ElTask.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        elif self.action in ("update", "partial_update"):
            return TaskUpdateSerializer
        elif self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.ok(
            content=serializer.data, http_status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
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

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """关闭任务"""
        task = self.get_object()
        if task.status == "closed":
            raise ApiException(
                msg="任务已关闭", code=ResponseStatus.ERROR.code
            )
        task.status = "closed"
        task.save(update_fields=["status"])
        ElTaskConversation.objects.create(
            task=task,
            content="任务已关闭",
            comment_type="system",
        )
        serializer = TaskDetailSerializer(task)
        return ApiResponse.ok(content=serializer.data)

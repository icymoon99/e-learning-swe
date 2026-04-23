"""任务记忆查询视图"""

from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_response import ApiResponse
from task.models import ElTaskMemory, ElTask
from task.serializers import TaskMemorySerializer
from task.filters import TaskMemoryFilterSet


class MemoryViewSet(viewsets.ViewSet):
    """任务记忆只读查询 ViewSet

    路由: GET /api/task/tasks/{task_id}/memories/
    """

    serializer_class = TaskMemorySerializer
    filterset_class = TaskMemoryFilterSet
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 记忆通常不多，全量返回

    def get_queryset(self):
        task_pk = self.kwargs.get("task_pk")
        try:
            ElTask.objects.get(id=task_pk)
        except ElTask.DoesNotExist:
            raise Http404(f"Task {task_pk} not found")
        return ElTaskMemory.objects.filter(
            task_id=task_pk
        ).order_by("execution_order")

    def list(self, request, task_pk=None):
        queryset = self.get_queryset()
        serializer = TaskMemorySerializer(queryset, many=True)
        return ApiResponse.ok(
            {"count": queryset.count(), "results": serializer.data}
        )

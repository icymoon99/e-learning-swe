from django.db.models import Q
from django_q.models import Task
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import TaskSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class TaskViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = None  # we use custom paginated_response

    def _get_queryset_by_status(self, status):
        if status == "success":
            return Task.objects.filter(success=True)
        elif status == "failure":
            return Task.objects.filter(success=False)
        elif status == "running":
            return Task.objects.filter(success__isnull=True)
        return Task.objects.all()

    def list(self, request, *args, **kwargs):
        status_filter = request.query_params.get("status")
        queryset = self._get_queryset_by_status(status_filter) if status_filter else Task.objects.all()

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)

        queryset = queryset.order_by("-started")

        return paginated_response(request, queryset, TaskSerializer, page_size=20)

    def retrieve(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            raise ApiException(msg="任务不存在", code=ResponseStatus.NOT_FOUND.code)

        serializer = TaskSerializer(task)
        return ApiResponse.ok(content=serializer.data)

    def destroy(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            from rest_framework.response import Response
            from rest_framework import status as drf_status
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            raise ApiException(msg="任务不存在", code=ResponseStatus.NOT_FOUND.code)

        task.delete()
        return ApiResponse.ok()

from django_q.models import Task
from rest_framework import mixins, permissions, status as drf_status, viewsets

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import StandardPagination
from q2.serializers import TaskSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class TaskViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        status_filter = self.request.query_params.get("status")
        if status_filter == "success":
            return Task.objects.filter(success=True)
        if status_filter == "failure":
            return Task.objects.filter(success=False)
        if status_filter == "running":
            return Task.objects.filter(success__isnull=True)
        return Task.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset.order_by("-started")

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            obj = queryset.get(id=self.kwargs[lookup_url_kwarg])
        except Task.DoesNotExist:
            raise ApiException(msg="任务不存在", code=ResponseStatus.NOT_FOUND.code)
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )
        instance = self.get_object()
        instance.delete()
        return ApiResponse.ok()

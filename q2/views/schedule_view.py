from django_q.models import Schedule
from rest_framework import mixins, permissions, status as drf_status, viewsets

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import ScheduleSerializer
from q2.views.task_view import IsAdminUser


class ScheduleViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer
    pagination_class = None

    def get_queryset(self):
        return Schedule.objects.all().order_by("-id")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return paginated_response(request, queryset, ScheduleSerializer, page_size=20)

    def create(self, request, *args, **kwargs):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            obj = queryset.get(pk=self.kwargs[lookup_url_kwarg])
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)
        self.check_object_permissions(self.request, obj)
        return obj

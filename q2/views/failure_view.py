import json

from django_q.models import Failure
from django_q.tasks import async_task
from rest_framework import mixins, status as drf_status, viewsets
from rest_framework.decorators import action

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from q2.serializers import TaskSerializer
from q2.views.task_view import IsAdminUser


class FailureViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Failure.objects.all().order_by("-stopped")

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
            obj = queryset.get(id=self.kwargs[lookup_url_kwarg])
        except Failure.DoesNotExist:
            raise ApiException(msg="失败任务不存在", code=ResponseStatus.NOT_FOUND.code)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        instance = self.get_object()
        try:
            args = json.loads(instance.args) if instance.args else []
            kwargs = json.loads(instance.kwargs) if instance.kwargs else {}
            if not isinstance(args, (list, tuple)):
                args = (args,)
            new_task_id = async_task(instance.func, *args, **kwargs)
            instance.delete()
            return ApiResponse.ok(content={"task_id": new_task_id, "name": instance.name})
        except Exception as e:
            raise ApiException(msg=f"重试失败: {str(e)}", code=ResponseStatus.ERROR.code)

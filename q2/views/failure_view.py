from django_q.models import Failure
from django_q.tasks import async_task
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import TaskSerializer
from q2.views.task_view import IsAdminUser


class FailureViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = Failure.objects.all().order_by("-stopped")
        return paginated_response(request, queryset, TaskSerializer, page_size=20)

    def destroy(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            from rest_framework import status as drf_status
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        try:
            failure = Failure.objects.get(id=pk)
        except Failure.DoesNotExist:
            raise ApiException(msg="失败任务不存在", code=ResponseStatus.NOT_FOUND.code)

        failure.delete()
        return ApiResponse.ok()

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            from rest_framework import status as drf_status
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        try:
            failure = Failure.objects.get(id=pk)
        except Failure.DoesNotExist:
            raise ApiException(msg="失败任务不存在", code=ResponseStatus.NOT_FOUND.code)

        try:
            import json
            args = json.loads(failure.args) if failure.args else []
            kwargs = json.loads(failure.kwargs) if failure.kwargs else {}
            # Ensure args is a list/tuple
            if not isinstance(args, (list, tuple)):
                args = (args,)
            new_task_id = async_task(failure.func, *args, **kwargs)
            failure.delete()
            return ApiResponse.ok(content={"task_id": new_task_id, "name": failure.name})
        except Exception as e:
            raise ApiException(msg=f"重试失败: {str(e)}", code=ResponseStatus.ERROR.code)

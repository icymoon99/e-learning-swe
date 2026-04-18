from django_q.brokers import get_broker
from rest_framework import permissions, status as drf_status, viewsets
from rest_framework.decorators import action

from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from q2.views.task_view import IsAdminUser


class QueueViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        broker = get_broker()
        try:
            queue_size = broker.queue_size()
        except Exception:
            queue_size = 0

        return ApiResponse.ok(content={
            "worker_running": False,
            "queue_size": queue_size,
            "tasks_running": 0,
            "tasks_failed": 0,
        })

    @action(detail=False, methods=["post"], url_path="pause")
    def pause_queue(self, request):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        action_param = request.data.get("action")
        if action_param not in ("pause", "resume"):
            from core.common.exception.api_exception import ApiException
            raise ApiException(msg="action 必须为 pause 或 resume", code=ResponseStatus.PARAMETER_ERROR.code)

        broker = get_broker()
        try:
            if action_param == "pause":
                broker.enqueue("__pause__")
            else:
                broker.enqueue("__resume__")
        except Exception as e:
            from core.common.exception.api_exception import ApiException
            raise ApiException(msg=f"操作失败: {str(e)}", code=ResponseStatus.ERROR.code)

        return ApiResponse.ok(content={"action": action_param})

from django_q.models import Schedule
from rest_framework import permissions, viewsets
from rest_framework import status as drf_status

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import ScheduleSerializer
from q2.views.task_view import IsAdminUser


class ScheduleViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ScheduleSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = Schedule.objects.all().order_by("-id")
        return paginated_response(request, queryset, ScheduleSerializer, page_size=20)

    def create(self, request, *args, **kwargs):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        serializer = ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        schedule = Schedule.objects.create(
            name=serializer.validated_data["name"],
            func=serializer.validated_data["func"],
            schedule_type=serializer.validated_data["schedule_type"],
            minutes=serializer.validated_data.get("minutes"),
            repeats=serializer.validated_data.get("repeats", -1),
            args=serializer.validated_data.get("args", ""),
            kwargs=serializer.validated_data.get("kwargs", "{}"),
            cron=serializer.validated_data.get("cron"),
        )

        output = ScheduleSerializer(schedule)
        return ApiResponse.ok(content=output.data, http_status=201)

    def update(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        try:
            schedule = Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)

        serializer = ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        schedule.name = serializer.validated_data.get("name", schedule.name)
        schedule.func = serializer.validated_data.get("func", schedule.func)
        schedule.schedule_type = serializer.validated_data.get(
            "schedule_type", schedule.schedule_type
        )
        if "minutes" in serializer.validated_data:
            schedule.minutes = serializer.validated_data["minutes"]
        if "repeats" in serializer.validated_data:
            schedule.repeats = serializer.validated_data["repeats"]
        if "args" in serializer.validated_data:
            schedule.args = serializer.validated_data["args"]
        if "kwargs" in serializer.validated_data:
            schedule.kwargs = serializer.validated_data["kwargs"]
        if "cron" in serializer.validated_data:
            schedule.cron = serializer.validated_data["cron"]
        schedule.save()

        output = ScheduleSerializer(schedule)
        return ApiResponse.ok(content=output.data)

    def destroy(self, request, pk=None):
        if not IsAdminUser().has_permission(request, self):
            return ApiResponse(
                status=ResponseStatus.ERROR,
                message="需要管理员权限",
                http_status=drf_status.HTTP_403_FORBIDDEN,
            )

        try:
            schedule = Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)

        schedule.delete()
        return ApiResponse.ok()

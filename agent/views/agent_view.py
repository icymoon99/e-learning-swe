from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from core.common.exception.api_response import ApiResponse

from agent.filters import ElAgentFilter, ElAgentExecutionLogFilter
from agent.models import ElAgent, ElAgentExecutionLog
from agent.serializers import AgentSerializer, AgentExecutionLogSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """Agent 配置管理"""

    permission_classes = [IsAuthenticated]
    queryset = ElAgent.objects.all().order_by("-created_at")
    serializer_class = AgentSerializer
    filterset_class = ElAgentFilter
    search_fields = ["code", "name"]
    ordering_fields = ["created_at", "updated_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.ok(content=serializer.data, http_status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.ok(content=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.ok(message="删除成功", http_status=status.HTTP_200_OK)


class AgentExecutionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Agent 执行日志查询"""

    permission_classes = [IsAuthenticated]
    queryset = ElAgentExecutionLog.objects.select_related("agent").order_by(
        "-created_at"
    )
    serializer_class = AgentExecutionLogSerializer
    filterset_class = ElAgentExecutionLogFilter
    search_fields = ["thread_id"]
    ordering_fields = ["created_at", "updated_at"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(content=serializer.data)

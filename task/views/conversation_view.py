from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import StandardPagination
from task.models import ElTask, ElTaskConversation
from task.serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
)


class ConversationViewSet(viewsets.GenericViewSet):
    """任务对话/指令管理（嵌套在 task 下）"""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        task_id = self.kwargs.get("task_pk")
        return ElTaskConversation.objects.filter(
            task_id=task_id
        ).order_by("created_at")

    def list(self, request, task_pk=None):
        """获取对话流"""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ConversationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ConversationSerializer(queryset, many=True)
        return ApiResponse.ok(content=serializer.data)

    def create(self, request, task_pk=None):
        """发送指令（触发 Agent 执行）"""
        # 1. 校验任务
        try:
            task = ElTask.objects.get(id=task_pk)
        except ElTask.DoesNotExist:
            raise ApiException(
                msg="任务不存在", code=ResponseStatus.ERROR.code
            )

        if task.status == "closed":
            raise ApiException(
                msg="任务已关闭，无法发送指令",
                code=ResponseStatus.ERROR.code,
            )

        # 2. 校验请求体
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        content = serializer.validated_data["content"]
        agent_code = serializer.validated_data["agent_code"]

        # 3. 校验 Agent
        from agent.models import ElAgent
        try:
            agent = ElAgent.objects.get(code=agent_code)
        except ElAgent.DoesNotExist:
            raise ApiException(
                msg=f"Agent '{agent_code}' 不存在",
                code=ResponseStatus.PARAMETER_ERROR.code,
            )

        # 4. 创建用户指令对话
        conv = ElTaskConversation.objects.create(
            task=task,
            content=content,
            comment_type="user",
            agent_code=agent_code,
        )

        # 5. 创建执行日志（running）
        from agent.models import ElAgentExecutionLog
        thread_id = f"task-{task.id}-{conv.id}"
        execution_log = ElAgentExecutionLog.objects.create(
            agent=agent,
            thread_id=thread_id,
            status="running",
        )

        # 6. 异步执行
        from django_q.tasks import async_task

        # 从仓库源获取 Token 实际值
        git_token = ""
        if task.git_source:
            git_token = task.git_source.token

        async_task(
            "task.tasks.execute_task_conversation",
            str(conv.id),
            agent_code,
            str(task.id),
            str(execution_log.id),
            git_token,
        )

        result_serializer = ConversationSerializer(conv)
        result_data = result_serializer.data
        result_data["execution_log_id"] = str(execution_log.id)
        return ApiResponse.ok(content=result_data)

from rest_framework import serializers
from agent.models import ElAgent, ElAgentExecutionLog


class AgentSerializer(serializers.ModelSerializer):
    """Agent 配置序列化器"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ElAgent
        fields = [
            "id", "code", "name", "description", "system_prompt",
            "model", "status", "status_display", "metadata",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentExecutionLogSerializer(serializers.ModelSerializer):
    """Agent 执行日志序列化器"""

    agent_code = serializers.CharField(source="agent.code", read_only=True)
    agent_name = serializers.CharField(source="agent.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ElAgentExecutionLog
        fields = [
            "id", "agent", "agent_code", "agent_name", "thread_id",
            "status", "status_display", "events", "result", "error_message",
            "git_pr_url", "git_pr_number", "git_commit_hash",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "git_pr_url", "git_pr_number", "git_commit_hash",
        ]

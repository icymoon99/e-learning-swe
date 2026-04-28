from rest_framework import serializers
from agent.models import ElAgent, ElAgentExecutionLog, ElExecutor
from agent.schemas import EXECUTOR_SCHEMAS


class AgentSerializer(serializers.ModelSerializer):
    """Agent 配置序列化器"""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    llm_model_display = serializers.SerializerMethodField(read_only=True)
    executor_display = serializers.SerializerMethodField(read_only=True)
    sandbox_instance_name = serializers.SerializerMethodField(read_only=True)
    sandbox_instance_status = serializers.SerializerMethodField(read_only=True)

    def get_llm_model_display(self, obj):
        if obj.llm_model:
            return f"{obj.llm_model.provider.name} · {obj.llm_model.display_name}"
        return ""

    def get_executor_display(self, obj):
        return obj.executor.name if obj.executor else ""

    def get_sandbox_instance_name(self, obj):
        return obj.sandbox_instance.name if obj.sandbox_instance else ""

    def get_sandbox_instance_status(self, obj):
        return obj.sandbox_instance.get_status_display() if obj.sandbox_instance else ""

    class Meta:
        model = ElAgent
        fields = [
            "id", "code", "name", "description", "system_prompt",
            "llm_model", "llm_model_display", "executor", "executor_display",
            "sandbox_instance", "sandbox_instance_name", "sandbox_instance_status",
            "status", "status_display", "metadata",
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


def _merge_schema_with_values(code: str, db_metadata: dict) -> dict:
    """合并 code-defined schema 与 DB metadata 值。"""
    schema = EXECUTOR_SCHEMAS.get(code, {})
    result = {}
    for group_key, group_fields in schema.items():
        group_result = {}
        db_group = db_metadata.get(group_key, {})
        for field_key, field_def in group_fields.items():
            group_result[field_key] = {**field_def, "value": db_group.get(field_key, "")}
        result[group_key] = group_result
    return result


def _extract_values_from_schema(metadata_schema: dict) -> dict:
    """从前端提交的 metadata_schema 中提取 value 存回 DB。"""
    result = {}
    for group_key, group_fields in metadata_schema.items():
        group_result = {}
        for field_key, field_def in group_fields.items():
            if isinstance(field_def, dict) and "value" in field_def:
                group_result[field_key] = field_def["value"]
        if group_result:
            result[group_key] = group_result
    return result


class ExecutorSerializer(serializers.ModelSerializer):
    """执行器序列化器。

    GET: 返回 metadata_schema（合并 schema 定义 + DB 值）
    PUT: 从 metadata_schema 提取 value 存回 metadata
    code/name/timeout 为只读字段
    """

    metadata_schema = serializers.SerializerMethodField(read_only=True)
    metadata_schema_input = serializers.JSONField(write_only=True, required=False, source='metadata')

    class Meta:
        model = ElExecutor
        fields = ["id", "code", "name", "enabled", "timeout", "metadata_schema", "metadata_schema_input"]
        read_only_fields = ["id", "code", "name", "timeout"]

    def get_metadata_schema(self, obj) -> dict:
        """合并 schema 定义与 DB 值。"""
        return _merge_schema_with_values(obj.code, obj.metadata)

    def update(self, instance, validated_data):
        metadata_input = validated_data.pop('metadata', None)
        if metadata_input is not None:
            instance.metadata = _extract_values_from_schema(metadata_input)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

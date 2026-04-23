from rest_framework import serializers

from task.models import ElTask, ElTaskConversation, ElTaskMemory, TASK_STATUS_CHOICES


class GitSourceNestedSerializer(serializers.Serializer):
    """任务详情中嵌套的仓库源信息"""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    platform = serializers.CharField(read_only=True)
    platform_display = serializers.CharField(read_only=True)
    repo_url = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "platform": instance.platform,
            "platform_display": instance.get_platform_display(),
            "repo_url": instance.repo_url,
        }


class TaskSerializer(serializers.ModelSerializer):
    """任务序列化器（列表）"""

    git_source_name = serializers.CharField(
        source="git_source.name", read_only=True
    )
    platform = serializers.CharField(
        source="git_source.platform", read_only=True
    )
    status_display = serializers.SerializerMethodField()
    latest_execution_status = serializers.SerializerMethodField()
    latest_execution_agent = serializers.SerializerMethodField()

    class Meta:
        model = ElTask
        fields = [
            "id", "title", "git_source_name", "platform",
            "status", "status_display", "source_branch",
            "latest_execution_status", "latest_execution_agent",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_status_display(self, obj):
        return dict(TASK_STATUS_CHOICES).get(obj.status, obj.status)

    def _get_latest_ai_conversation(self, obj):
        return (
            obj.conversations
            .filter(comment_type="ai", execution_log__isnull=False)
            .select_related("execution_log")
            .order_by("-created_at")
            .first()
        )

    def get_latest_execution_status(self, obj):
        conv = self._get_latest_ai_conversation(obj)
        if conv and conv.execution_log:
            return conv.execution_log.status
        return None

    def get_latest_execution_agent(self, obj):
        conv = self._get_latest_ai_conversation(obj)
        if conv and conv.agent_code:
            return conv.agent_code
        return None


class TaskDetailSerializer(serializers.ModelSerializer):
    """任务详情序列化器"""

    git_source = GitSourceNestedSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    latest_execution_status = serializers.SerializerMethodField()

    class Meta:
        model = ElTask
        fields = [
            "id", "title", "description", "git_source",
            "source_branch", "status", "status_display",
            "latest_execution_status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_status_display(self, obj):
        return dict(TASK_STATUS_CHOICES).get(obj.status, obj.status)

    def get_latest_execution_status(self, obj):
        conv = (
            obj.conversations
            .filter(comment_type="ai", execution_log__isnull=False)
            .select_related("execution_log")
            .order_by("-created_at")
            .first()
        )
        if conv and conv.execution_log:
            return conv.execution_log.status
        return None


class TaskCreateSerializer(serializers.ModelSerializer):
    """任务创建序列化器"""

    git_source_id = serializers.CharField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = ElTask
        fields = ["id", "title", "description", "git_source_id", "source_branch"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        git_source_id = validated_data.pop("git_source_id", None)
        if git_source_id:
            from git_source.models import ElGitSource
            validated_data["git_source"] = ElGitSource.objects.get(id=git_source_id)
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """任务更新序列化器"""

    class Meta:
        model = ElTask
        fields = ["title", "description", "source_branch"]


class ConversationSerializer(serializers.ModelSerializer):
    """任务对话序列化器"""

    comment_type_display = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()
    execution_status = serializers.SerializerMethodField()

    class Meta:
        model = ElTaskConversation
        fields = [
            "id", "content", "comment_type", "comment_type_display",
            "agent_code", "agent_name",
            "execution_log_id", "execution_status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_comment_type_display(self, obj):
        return obj.get_comment_type_display()

    def get_agent_name(self, obj):
        if not obj.agent_code:
            return None
        try:
            from agent.models import ElAgent
            agent = ElAgent.objects.get(code=obj.agent_code)
            return agent.name
        except ElAgent.DoesNotExist:
            return obj.agent_code

    def get_execution_status(self, obj):
        if obj.execution_log:
            return obj.execution_log.status
        return None


class ConversationCreateSerializer(serializers.Serializer):
    """发送指令请求体"""

    content = serializers.CharField(required=True)
    agent_code = serializers.CharField(required=True, max_length=128)


class TaskMemorySerializer(serializers.ModelSerializer):
    """任务记忆序列化器"""

    agent_name = serializers.CharField(
        source="agent.name", read_only=True, allow_null=True
    )

    class Meta:
        model = ElTaskMemory
        fields = [
            "id",
            "agent_name",
            "execution_order",
            "summary",
            "commit_message",
            "pr_url",
            "commit_hash",
            "status",
            "error_message",
            "created_at",
        ]
        read_only_fields = fields

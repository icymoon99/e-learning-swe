from rest_framework import serializers

from .models import ElGitSource


class GitSourceSerializer(serializers.ModelSerializer):
    """仓库源序列化器（列表/详情）"""

    platform_display = serializers.CharField(
        source="get_platform_display", read_only=True
    )

    class Meta:
        model = ElGitSource
        fields = [
            "id", "name", "platform", "platform_display",
            "repo_url", "default_branch", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "token": {"write_only": True},
        }


class GitSourceCreateUpdateSerializer(serializers.ModelSerializer):
    """仓库源创建/更新序列化器"""

    class Meta:
        model = ElGitSource
        fields = [
            "id", "name", "platform", "repo_url",
            "token", "default_branch", "description",
        ]
        read_only_fields = ["id"]


class GitSourceDropdownSerializer(serializers.ModelSerializer):
    """仓库源下拉选项（精简字段）"""

    platform_display = serializers.CharField(
        source="get_platform_display", read_only=True
    )

    class Meta:
        model = ElGitSource
        fields = ["id", "name", "platform", "platform_display", "repo_url", "default_branch"]

from rest_framework import serializers

from .models import ElLLMProvider, ElLLMModel


class ElLLMProviderSerializer(serializers.ModelSerializer):
    """LLM 供应商序列化器（列表/详情）"""

    resolved_base_url = serializers.CharField(read_only=True)

    class Meta:
        model = ElLLMProvider
        fields = [
            "id", "code", "name", "base_url", "resolved_base_url",
            "enabled", "description", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ElLLMProviderCreateSerializer(serializers.ModelSerializer):
    """LLM 供应商创建/更新序列化器"""

    class Meta:
        model = ElLLMProvider
        fields = ["id", "code", "name", "base_url", "api_key_encrypted", "enabled", "description"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "api_key_encrypted": {"write_only": True},
        }


class ElLLMModelSerializer(serializers.ModelSerializer):
    """LLM 模型序列化器"""

    provider_name = serializers.CharField(source="provider.name", read_only=True)
    provider_code = serializers.CharField(source="provider.code", read_only=True)

    class Meta:
        model = ElLLMModel
        fields = [
            "id", "provider", "provider_name", "provider_code",
            "model_code", "display_name", "context_window",
            "max_output_tokens", "enabled", "sort_order", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ElLLMModelDropdownSerializer(serializers.ModelSerializer):
    """LLM 模型下拉选项（精简字段，含嵌套供应商信息）"""

    provider_name = serializers.CharField(source="provider.name", read_only=True)
    provider_code = serializers.CharField(source="provider.code", read_only=True)

    class Meta:
        model = ElLLMModel
        fields = ["id", "model_code", "display_name", "provider_name", "provider_code", "enabled"]

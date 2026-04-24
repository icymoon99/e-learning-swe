from rest_framework import serializers

from sandbox.models import ElSandboxInstance, SANDBOX_TYPES, STATUS_CHOICES


class SandboxInstanceSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ElSandboxInstance
        fields = [
            "id",
            "name",
            "type",
            "type_display",
            "status",
            "status_display",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        sandbox_type = data.get("type")
        metadata = data.get("metadata", {})

        if sandbox_type in ("localdocker", "remotedocker") and "image" not in metadata:
            metadata.setdefault("image", "sandbox:latest")

        if sandbox_type and sandbox_type.startswith("remote"):
            if "ssh_host" not in metadata:
                raise serializers.ValidationError(
                    {"metadata": "远程模式需要提供 ssh_host"}
                )
            if not (
                metadata.get("ssh_key_path") or metadata.get("ssh_password")
            ):
                raise serializers.ValidationError(
                    {"metadata": "远程模式需要提供 ssh_key_path 或 ssh_password 至少一个"}
                )

        return data

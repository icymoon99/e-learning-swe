from rest_framework import status, viewsets
from rest_framework.decorators import action

from core.common.exception.api_response import ApiResponse
from sandbox.filters import SandboxInstanceFilter
from sandbox.models import ElSandboxInstance
from sandbox.serializers import SandboxInstanceSerializer
from sandbox.services import SandboxService


class SandboxInstanceViewSet(viewsets.ModelViewSet):
    """沙箱实例 CRUD"""

    queryset = ElSandboxInstance.objects.all()
    serializer_class = SandboxInstanceSerializer
    filterset_class = SandboxInstanceFilter
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "type", "status"]
    ordering = ["-created_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.ok(serializer.data, http_status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.ok(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.ok(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = str(instance.id)
        service = SandboxService()
        service.delete(instance)
        self.perform_destroy(instance)
        return ApiResponse.ok(content={"id": instance_id})

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        instance = self.get_object()
        service = SandboxService()
        service.start(instance)
        return ApiResponse.ok(content={"status": instance.status})

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        instance = self.get_object()
        service = SandboxService()
        service.stop(instance)
        return ApiResponse.ok(content={"status": instance.status})

    @action(detail=True, methods=["post"])
    def reset(self, request, pk=None):
        instance = self.get_object()
        service = SandboxService()
        service.reset(instance)
        return ApiResponse.ok(content={"message": "沙箱已重置"})

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        instance = self.get_object()
        command = request.data.get("command")
        if not command:
            return ApiResponse.parameter_error(message="command 参数不能为空")

        timeout = request.data.get("timeout")
        service = SandboxService()
        backend = service.get_backend(instance)

        response = backend.execute(command, timeout=timeout)
        return ApiResponse.ok(
            content={
                "output": response.output,
                "exit_code": response.exit_code,
                "truncated": response.truncated,
            }
        )

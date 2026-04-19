"""序列化器和过滤器测试"""
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from sandbox.models import ElSandboxInstance
from sandbox.serializers import SandboxInstanceSerializer


class TestSandboxInstanceSerializer(TestCase):
    def test_create_valid_localdocker(self):
        data = {
            "name": "serializer-test",
            "type": "localdocker",
            "root_path": "/workspace",
            "metadata": {"image": "sandbox:latest", "work_dir": "/workspace"},
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.name, "serializer-test")

    def test_remote_requires_ssh_host(self):
        data = {
            "name": "remote-no-host",
            "type": "remotesystem",
            "root_path": "/home/sandbox",
            "metadata": {"work_dir": "/home/sandbox"},
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("metadata", serializer.errors)

    def test_read_only_fields(self):
        instance = ElSandboxInstance.objects.create(
            name="readonly-test",
            type="localsystem",
            root_path="/test",
        )
        serializer = SandboxInstanceSerializer(instance)
        self.assertIn("id", serializer.data)
        self.assertIn("type_display", serializer.data)
        self.assertIn("status_display", serializer.data)

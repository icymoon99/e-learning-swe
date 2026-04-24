"""序列化器和过滤器测试"""
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError

from sandbox.models import ElSandboxInstance
from sandbox.serializers import SandboxInstanceSerializer


class TestSandboxInstanceSerializer(TestCase):
    def test_create_valid_localdocker(self):
        """创建 localdocker 实例（无 root_path）"""
        data = {
            "name": "serializer-test",
            "type": "localdocker",
            "metadata": {"image": "sandbox:latest", "work_dir": "/workspace"},
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.name, "serializer-test")

    def test_remote_requires_ssh_host(self):
        """远程类型必须有 ssh_host"""
        data = {
            "name": "remote-no-host",
            "type": "remotesystem",
            "metadata": {"work_dir": "/home/sandbox"},
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("metadata", serializer.errors)

    def test_remote_requires_ssh_auth(self):
        """远程类型必须有 ssh_key_path 或 ssh_password 至少一个"""
        data = {
            "name": "remote-no-auth",
            "type": "remotesystem",
            "metadata": {
                "ssh_host": "10.0.0.1",
                "work_dir": "/workspace",
            },
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("metadata", serializer.errors)

    def test_remote_with_ssh_key_path_valid(self):
        """远程类型提供 ssh_key_path 应通过校验"""
        data = {
            "name": "remote-with-key",
            "type": "remotesystem",
            "metadata": {
                "ssh_host": "10.0.0.1",
                "work_dir": "/workspace",
                "ssh_key_path": "/home/user/.ssh/id_rsa",
            },
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_remote_with_ssh_password_valid(self):
        """远程类型提供 ssh_password 应通过校验"""
        data = {
            "name": "remote-with-pwd",
            "type": "remotesystem",
            "metadata": {
                "ssh_host": "10.0.0.1",
                "work_dir": "/workspace",
                "ssh_password": "secret123",
            },
        }
        serializer = SandboxInstanceSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_read_only_fields(self):
        """序列化输出包含 id、type_display、status_display"""
        instance = ElSandboxInstance.objects.create(
            name="readonly-test",
            type="localsystem",
            metadata={"root_path": "/test", "work_dir": "/workspace"},
        )
        serializer = SandboxInstanceSerializer(instance)
        self.assertIn("id", serializer.data)
        self.assertIn("type_display", serializer.data)
        self.assertIn("status_display", serializer.data)
        self.assertNotIn("root_path", serializer.data)

    def test_root_path_not_in_fields(self):
        """序列化器的 fields 不应包含 root_path"""
        self.assertNotIn("root_path", SandboxInstanceSerializer.Meta.fields)

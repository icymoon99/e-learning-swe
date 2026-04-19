"""沙箱实例模型测试"""
from django.test import TestCase
from django.core.exceptions import ValidationError

from sandbox.models import ElSandboxInstance, SANDBOX_TYPES


class TestSandboxInstanceModel(TestCase):
    def test_create_localdocker(self):
        """创建本地 Docker 沙箱实例"""
        instance = ElSandboxInstance.objects.create(
            name="test-docker",
            type="localdocker",
            root_path="/workspace",
            status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )
        self.assertEqual(instance.name, "test-docker")
        self.assertEqual(instance.type, "localdocker")
        self.assertEqual(instance.status, "active")
        self.assertEqual(instance.metadata["image"], "sandbox:latest")

    def test_create_remotesystem_with_encrypted_fields(self):
        """创建远程系统沙箱，metadata 包含加密字段"""
        instance = ElSandboxInstance.objects.create(
            name="remote-sys",
            type="remotesystem",
            root_path="/home/sandbox",
            metadata={
                "work_dir": "/home/sandbox",
                "ssh_host": "10.0.0.1",
                "ssh_port": 22,
                "ssh_user": "admin",
                "ssh_password_enc": "base64_encrypted_value",
            },
        )
        self.assertEqual(instance.metadata["ssh_host"], "10.0.0.1")
        self.assertIn("ssh_password_enc", instance.metadata)

    def test_create_all_sandbox_types(self):
        """4 种沙箱类型均可正常创建"""
        for type_code, _ in SANDBOX_TYPES:
            instance = ElSandboxInstance.objects.create(
                name=f"test-{type_code}",
                type=type_code,
                root_path="/test",
            )
            self.assertEqual(instance.type, type_code)

    def test_default_status_is_inactive(self):
        """不指定 status 时，默认为 inactive"""
        instance = ElSandboxInstance.objects.create(
            name="default-status",
            type="localsystem",
            root_path="/test",
        )
        self.assertEqual(instance.status, "inactive")

    def test_default_metadata_is_empty_dict(self):
        """不指定 metadata 时，默认为空 dict"""
        instance = ElSandboxInstance.objects.create(
            name="default-meta",
            type="localsystem",
            root_path="/test",
        )
        self.assertIsInstance(instance.metadata, dict)
        self.assertEqual(len(instance.metadata), 0)

    def test_str_representation(self):
        """__str__ 包含名称和类型显示"""
        instance = ElSandboxInstance.objects.create(
            name="my-sandbox",
            type="localdocker",
            root_path="/test",
        )
        s = str(instance)
        self.assertIn("my-sandbox", s)
        self.assertIn("本地 Docker", s)

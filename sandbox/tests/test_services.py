"""服务层测试"""
import os
import tempfile
import shutil

from django.test import TestCase
from unittest.mock import patch, MagicMock

from sandbox.models import ElSandboxInstance
from sandbox.services import SandboxService
from sandbox.backends import LocalSystemBackend


class TestSandboxService(TestCase):
    def test_start_localsystem(self):
        """本地系统沙箱启动应创建目录并更新状态"""
        test_dir = tempfile.mkdtemp(prefix="service_test_")

        instance = ElSandboxInstance.objects.create(
            name="service-test",
            type="localsystem",
            root_path=test_dir,
            status="inactive",
        )

        service = SandboxService()
        service.start(instance)

        instance.refresh_from_db()
        self.assertEqual(instance.status, "active")

        shutil.rmtree(test_dir, ignore_errors=True)

    def test_reset_localsystem(self):
        """重置本地系统沙箱应清空目录"""
        test_dir = tempfile.mkdtemp(prefix="service_test_")
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("hello")

        instance = ElSandboxInstance.objects.create(
            name="reset-test",
            type="localsystem",
            root_path=test_dir,
            status="active",
        )

        service = SandboxService()
        service.reset(instance)

        self.assertFalse(os.path.exists(test_file))
        shutil.rmtree(test_dir, ignore_errors=True)

    def test_get_backend(self):
        """get_backend 返回正确类型"""
        instance = ElSandboxInstance.objects.create(
            name="get-backend-test",
            type="localsystem",
            root_path="/tmp",
        )
        service = SandboxService()
        backend = service.get_backend(instance)
        self.assertIsInstance(backend, LocalSystemBackend)

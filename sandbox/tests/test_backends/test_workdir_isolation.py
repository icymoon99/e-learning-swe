"""沙箱工作目录隔离测试 — 数据迁移 + 工厂函数 thread_id 隔离 + 各后端隔离行为"""

from django.test import TransactionTestCase
from sandbox.models import ElSandboxInstance
from sandbox.migrations._workdir_utils import migrate_absolute_to_relative
from sandbox.backends import get_backend


class TestGetBackendThreadIsolation:
    """测试 get_backend(instance, thread_id) 的 work_dir 隔离行为"""

    def test_no_thread_id_returns_original_work_dir(self):
        """不传 thread_id 时 work_dir 不变"""
        instance = ElSandboxInstance(
            name="test", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        backend = get_backend(instance)
        assert backend._work_dir == "workspace"

    def test_with_thread_id_appends_suffix(self):
        """传入 thread_id 时 work_dir 追加 -{thread_id} 后缀"""
        instance = ElSandboxInstance(
            name="test", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        backend = get_backend(instance, thread_id="abc123")
        assert backend._work_dir == "workspace-abc123"

    def test_empty_string_thread_id_no_isolation(self):
        """空字符串 thread_id 不隔离"""
        instance = ElSandboxInstance(
            name="test", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        backend = get_backend(instance, thread_id="")
        assert backend._work_dir == "workspace"

    def test_docker_backend_isolation(self):
        """Docker 后端同样应用隔离后缀"""
        instance = ElSandboxInstance(
            name="test", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "workspace"},
        )
        backend = get_backend(instance, thread_id="xyz789")
        assert backend._work_dir == "workspace-xyz789"

    def test_remotedocker_isolation(self):
        """远程 Docker 后端同样应用隔离后缀"""
        instance = ElSandboxInstance(
            name="test", type="remotedocker", status="active",
            metadata={
                "image": "sandbox:latest",
                "work_dir": "workspace",
                "ssh_host": "test.example.com",
                "ssh_user": "test",
                "ssh_password": "test",
            },
        )
        backend = get_backend(instance, thread_id="thread-001")
        assert backend._work_dir == "workspace-thread-001"

    def test_remotesystem_isolation(self):
        """远程 System 后端同样应用隔离后缀"""
        instance = ElSandboxInstance(
            name="test", type="remotesystem", status="active",
            metadata={
                "root_path": "sandbox/",
                "work_dir": "workspace",
                "ssh_host": "test.example.com",
                "ssh_user": "test",
                "ssh_password": "test",
            },
        )
        backend = get_backend(instance, thread_id="thread-002")
        assert backend._work_dir == "workspace-thread-002"


class TestLocalSystemBackendRootPath:
    """测试 LocalSystemBackend 的 root_path + work_dir 路径拼接"""

    def test_build_cmd_joins_root_path_and_work_dir(self):
        """_build_cmd 应使用 {root_path}/{work_dir} 拼接路径"""
        from sandbox.backends.local_system import LocalSystemBackend

        backend = LocalSystemBackend(
            name="test", root_path="sandbox/", work_dir="workspace-abc123"
        )
        cmd = backend._build_cmd("echo hello")
        assert "cd" in cmd
        assert "sandbox/workspace-abc123" in cmd

    def test_ensure_dir_creates_joined_path(self):
        """ensure_dir 应创建 {root_path}/{work_dir} 目录"""
        import tempfile
        import os
        import shutil
        from sandbox.backends.local_system import LocalSystemBackend

        tmp = tempfile.mkdtemp()
        try:
            root = os.path.join(tmp, "sandbox/")
            backend = LocalSystemBackend(name="test", root_path=root, work_dir="workspace-test")
            backend.ensure_dir()
            assert os.path.isdir(os.path.join(root, "workspace-test"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_reset_clears_only_isolated_dir(self):
        """reset 应仅清空拼接后的隔离目录"""
        import tempfile
        import os
        import shutil
        from sandbox.backends.local_system import LocalSystemBackend

        tmp = tempfile.mkdtemp()
        try:
            root = os.path.join(tmp, "sandbox")
            os.makedirs(root, exist_ok=True)
            # 在 root 下创建另一个不应被清空的文件
            other_file = os.path.join(root, "other.txt")
            with open(other_file, "w") as f:
                f.write("keep me")

            backend = LocalSystemBackend(name="test", root_path=root, work_dir="workspace-reset")
            backend.ensure_dir()
            test_file = os.path.join(root, "workspace-reset", "test.txt")
            with open(test_file, "w") as f:
                f.write("delete me")

            backend.reset()

            # 其他文件应仍然存在
            assert os.path.exists(other_file)
            # 隔离目录应存在但内容被清空
            assert os.path.isdir(os.path.join(root, "workspace-reset"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestRemoteSystemBackendRootPath:
    """测试 RemoteSystemBackend 的 root_path + work_dir 路径拼接"""

    def test_build_cmd_joins_root_path_and_work_dir(self):
        """_build_cmd 应使用 {root_path}/{work_dir} 拼接路径"""
        from sandbox.backends.remote_system import RemoteSystemBackend
        from sandbox.executors import SSHConfig

        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteSystemBackend(
            name="test", root_path="sandbox/", ssh_config=ssh_config, work_dir="workspace-xyz"
        )
        cmd = backend._build_cmd("echo hello")
        assert "cd" in cmd
        assert "sandbox/workspace-xyz" in cmd

    def test_ensure_dir_creates_joined_path(self):
        """ensure_dir 应创建 {root_path}/{work_dir} 目录"""
        from unittest.mock import patch
        from sandbox.backends.remote_system import RemoteSystemBackend
        from sandbox.executors import SSHConfig

        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteSystemBackend(
            name="test", root_path="remote_root/", ssh_config=ssh_config, work_dir="work"
        )
        with patch("sandbox.backends.remote_system.execute_remote") as mock_exec:
            backend.ensure_dir()
            call_args = mock_exec.call_args[0][0]
            assert "remote_root/work" in call_args


class TestWorkDirDataMigration(TransactionTestCase):
    """测试 0003_migrate_workdir_to_relative 迁移

    使用 TransactionTestCase 因为迁移操作需要在事务外运行。
    """

    def test_absolute_work_dir_stripped_leading_slash(self):
        """System 类型的绝对路径 work_dir 和 root_path 应去掉前导 /"""
        instance = ElSandboxInstance.objects.create(
            name="with-abs", type="localsystem", status="active",
            metadata={"root_path": "/tmp/", "work_dir": "/workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertFalse(instance.metadata["work_dir"].startswith("/"))
        self.assertEqual(instance.metadata["work_dir"], "workspace")
        self.assertFalse(instance.metadata["root_path"].startswith("/"))

    def test_docker_work_dir_stripped(self):
        """Docker 类型的绝对路径 work_dir 应去掉前导 /"""
        instance = ElSandboxInstance.objects.create(
            name="docker-abs", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertEqual(instance.metadata["work_dir"], "workspace")

    def test_relative_paths_unchanged(self):
        """已经是相对路径的不应被修改"""
        instance = ElSandboxInstance.objects.create(
            name="already-relative", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertEqual(instance.metadata["work_dir"], "workspace")
        self.assertEqual(instance.metadata["root_path"], "sandbox/")

    def test_migration_fails_on_empty_workdir(self):
        """work_dir 为空（去掉了 / 后）时应抛出 ValueError"""
        ElSandboxInstance.objects.create(
            name="empty-workdir", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/"},
        )
        with self.assertRaises(ValueError) as ctx:
            migrate_absolute_to_relative(ElSandboxInstance)
        self.assertIn("work_dir 为空", str(ctx.exception))

    def test_migration_fails_on_dotdot_path(self):
        """work_dir 包含 .. 时迁移应失败"""
        ElSandboxInstance.objects.create(
            name="dotdot", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "../../../etc"},
        )
        with self.assertRaises(ValueError) as ctx:
            migrate_absolute_to_relative(ElSandboxInstance)
        self.assertIn("work_dir 包含 ..", str(ctx.exception))

    def test_no_instance_left_with_absolute_path(self):
        """迁移后数据库中不应存在任何绝对路径"""
        ElSandboxInstance.objects.create(
            name="abs-1", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )
        ElSandboxInstance.objects.create(
            name="abs-2", type="localsystem", status="active",
            metadata={"root_path": "/home/user/", "work_dir": "/tmp/work"},
        )
        ElSandboxInstance.objects.create(
            name="rel-1", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        for inst in ElSandboxInstance.objects.all():
            if "work_dir" in inst.metadata:
                self.assertFalse(
                    inst.metadata["work_dir"].startswith("/"),
                    f"{inst.name} 仍有绝对路径 work_dir"
                )
            if inst.type in ("localsystem", "remotesystem"):
                if "root_path" in inst.metadata:
                    self.assertFalse(
                        inst.metadata["root_path"].startswith("/"),
                        f"{inst.name} 仍有绝对路径 root_path"
                    )

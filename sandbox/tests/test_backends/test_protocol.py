"""验证沙箱后端与 deepagents SandboxBackendProtocol 的接口契约一致性。"""

import os
import shutil
import tempfile
import unittest

from deepagents.backends.protocol import SandboxBackendProtocol

from sandbox.backends import (
    LocalDockerBackend,
    LocalSystemBackend,
    RemoteDockerBackend,
    RemoteSystemBackend,
    get_backend,
)
from sandbox.executors import SSHConfig
from sandbox.models import ElSandboxInstance


class TestProtocolCompliance(unittest.TestCase):
    """确保所有后端类实现 SandboxBackendProtocol 要求的每个方法。"""

    REQUIRED_METHODS = [
        "id",
        "execute",
        "read",
        "write",
        "edit",
        "ls",
        "ls_info",
        "glob",
        "glob_info",
        "grep",
        "grep_raw",
        "upload_files",
        "download_files",
    ]

    def _check_protocol(self, backend_class):
        for attr in self.REQUIRED_METHODS:
            self.assertTrue(
                hasattr(backend_class, attr),
                f"{backend_class.__name__} 缺少协议方法: {attr}",
            )

    def test_local_docker_protocol(self):
        self._check_protocol(LocalDockerBackend)

    def test_remote_docker_protocol(self):
        self._check_protocol(RemoteDockerBackend)

    def test_local_system_protocol(self):
        self._check_protocol(LocalSystemBackend)

    def test_remote_system_protocol(self):
        self._check_protocol(RemoteSystemBackend)


class TestLocalSystemBackend(unittest.TestCase):
    """LocalSystemBackend 功能测试 — 最简单的后端类型"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sandbox_test_")
        self.backend = LocalSystemBackend(
            name="test", root_path=self.test_dir, work_dir=self.test_dir
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_id_property(self):
        self.assertEqual(self.backend.id, "local-system-test")

    def test_execute_command(self):
        response = self.backend.execute("echo hello")
        self.assertEqual(response.exit_code, 0)
        self.assertIn("hello", response.output)

    def test_write_and_read_file(self):
        test_file = f"{self.test_dir}/test.txt"
        write_result = self.backend.write(test_file, "hello world")
        self.assertIsNone(write_result.error)

        content = self.backend.read(test_file)
        self.assertIn("hello world", content)

    def test_edit_file(self):
        test_file = f"{self.test_dir}/edit.txt"
        self.backend.write(test_file, "hello world")
        result = self.backend.edit(test_file, "hello", "goodbye")
        self.assertIsNone(result.error)

        content = self.backend.read(test_file)
        self.assertIn("goodbye world", content)

    def test_edit_file_not_found(self):
        result = self.backend.edit("/nonexistent/file.txt", "old", "new")
        self.assertIsNotNone(result.error)

    def test_ls_info(self):
        test_file = f"{self.test_dir}/listing.txt"
        self.backend.write(test_file, "test")
        entries = self.backend.ls_info(self.test_dir)
        paths = [e["path"] for e in entries]
        self.assertTrue(any("listing.txt" in p for p in paths))

    def test_glob(self):
        self.backend.write(f"{self.test_dir}/a.py", "pass")
        self.backend.write(f"{self.test_dir}/b.txt", "pass")
        matches = self.backend.glob("*.py", self.test_dir)
        self.assertEqual(len(matches["matches"]), 1)
        self.assertTrue(matches["matches"][0].endswith("a.py"))

    def test_grep(self):
        self.backend.write(f"{self.test_dir}/search.txt", "hello world\ntest line")
        result = self.backend.grep("hello", self.test_dir)
        self.assertEqual(len(result["matches"]), 1)
        self.assertIn("hello", result["matches"][0]["content"])

    def test_download_file_not_found(self):
        responses = self.backend.download_files(["/nonexistent/path"])
        self.assertEqual(responses[0].error, "file_not_found")

    def test_upload_files(self):
        responses = self.backend.upload_files(
            [(f"{self.test_dir}/upload.txt", b"uploaded content")]
        )
        self.assertIsNone(responses[0].error)

    def test_work_dir_used_in_build_cmd(self):
        """_build_cmd 应使用 work_dir 而非 root_path"""
        backend = LocalSystemBackend(
            name="test", root_path="/tmp", work_dir="/workspace"
        )
        cmd = backend._build_cmd("echo hello")
        self.assertIn("/workspace", cmd)
        self.assertNotIn("/tmp", cmd)

    def test_reset_clears_work_dir(self):
        """reset 应清空 work_dir 而非 root_path"""
        root_dir = tempfile.mkdtemp(prefix="sandbox_root_")
        work_dir = tempfile.mkdtemp(prefix="sandbox_work_")
        test_file = os.path.join(work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("data")

        backend = LocalSystemBackend(
            name="test", root_path=root_dir, work_dir=work_dir
        )
        backend.reset()

        self.assertFalse(os.path.exists(test_file))
        shutil.rmtree(root_dir, ignore_errors=True)
        shutil.rmtree(work_dir, ignore_errors=True)


class TestPathResolution(unittest.TestCase):
    """测试 _resolve_path 的虚拟路径转换行为"""

    def test_base_resolve_strips_leading_slash(self):
        """BaseSandboxBackend._resolve_path 应去掉前导 /"""
        backend = LocalDockerBackend(container_name="test", work_dir="workspace")
        resolved = backend._resolve_path("/src/main.py")
        self.assertEqual(resolved, "src/main.py")

    def test_local_docker_resolve_root(self):
        """根路径 / 应解析为 ."""
        backend = LocalDockerBackend(container_name="test", work_dir="workspace")
        resolved = backend._resolve_path("/")
        self.assertEqual(resolved, ".")

    def test_local_docker_resolve_subpath(self):
        """子路径 /src/main.py 应解析为相对于 work_dir 的路径"""
        backend = LocalDockerBackend(
            container_name="test", work_dir="workspace"
        )
        resolved = backend._resolve_path("/src/main.py")
        self.assertEqual(resolved, "src/main.py")

    def test_resolve_empty_path(self):
        """空路径或只有 / 应返回 ."""
        backend = LocalDockerBackend(container_name="test", work_dir="workspace")
        self.assertEqual(backend._resolve_path("/"), ".")
        self.assertEqual(backend._resolve_path(""), ".")


class TestBackendFactory(unittest.TestCase):
    def test_create_local_system_from_factory(self):
        instance = ElSandboxInstance(
            name="factory-test",
            type="localsystem",
            status="active",
            metadata={"root_path": "/tmp", "work_dir": "/tmp"},
        )
        backend = get_backend(instance)
        self.assertIsInstance(backend, LocalSystemBackend)

    def test_create_localdocker_from_factory(self):
        instance = ElSandboxInstance(
            name="docker-factory",
            type="localdocker",
            status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )
        backend = get_backend(instance)
        self.assertIsInstance(backend, LocalDockerBackend)

    def test_unknown_type_raises(self):
        instance = ElSandboxInstance(
            name="unknown",
            type="invalid_type",
        )
        with self.assertRaises(ValueError):
            get_backend(instance)

"""测试沙箱工作目录切换和路径遍历防护"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from core.common.exception.api_exception import ApiException
from sandbox.backends.local_system import LocalSystemBackend
from sandbox.backends.remote_system import RemoteSystemBackend
from sandbox.backends.local_docker import LocalDockerBackend
from sandbox.backends.remote_docker import RemoteDockerBackend
from sandbox.executors import SSHConfig


class TestLocalSystemBackendWorkDir(unittest.TestCase):
    """LocalSystemBackend 工作目录切换测试"""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix="sandbox_test_")
        self.root_path = self.base_dir
        self.work_dir = "workspace"
        self.full_work_dir = os.path.join(self.base_dir, "workspace")
        os.makedirs(self.full_work_dir, exist_ok=True)
        self.backend = LocalSystemBackend(
            name="test", root_path=self.root_path, work_dir=self.work_dir
        )

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def test_execute_cd_to_work_dir(self):
        """execute 应切换到 work_dir"""
        response = self.backend.execute("pwd")
        self.assertEqual(response.exit_code, 0)
        self.assertIn(self.full_work_dir, response.output.strip())

    def test_rm_restricted_to_work_dir(self):
        """rm -rf * 应被限制在 work_dir 内（不会删除项目根目录文件）"""
        test_file = os.path.join(self.full_work_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("data")

        self.backend.execute("rm -rf *")

        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(self.full_work_dir))


class TestRemoteSystemBackendWorkDir(unittest.TestCase):
    """RemoteSystemBackend 工作目录切换测试"""

    def test_execute_build_cmd_includes_cd(self):
        """_build_cmd_with_env(_build_cmd(cmd)) 应包含 cd"""
        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteSystemBackend(
            name="test", root_path="sandbox/", ssh_config=ssh_config, work_dir="workspace"
        )

        with patch("sandbox.backends.remote_system.execute_remote") as mock_exec:
            mock_exec.return_value = MagicMock(stdout="", stderr="", exit_code=0)
            backend.execute("echo hello")

            call_args = mock_exec.call_args[0][0]
            self.assertIn("cd sandbox/workspace", call_args)
            self.assertIn("echo hello", call_args)

    def test_execute_with_env_cd_after_export(self):
        """带环境变量时，cd 应在 export 之后"""
        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteSystemBackend(
            name="test", root_path="sandbox/", ssh_config=ssh_config, work_dir="workspace"
        )

        with patch("sandbox.backends.remote_system.execute_remote") as mock_exec:
            mock_exec.return_value = MagicMock(stdout="", stderr="", exit_code=0)
            backend.execute("echo hello", env={"KEY": "VALUE"})

            call_args = mock_exec.call_args[0][0]
            self.assertIn("export", call_args)
            self.assertIn("cd sandbox/workspace", call_args)
            cd_pos = call_args.index("cd sandbox/workspace")
            export_pos = call_args.index("export")
            self.assertGreater(cd_pos, export_pos)


class TestLocalDockerBackendWorkDir(unittest.TestCase):
    """LocalDockerBackend 工作目录切换测试"""

    def test_build_cmd_includes_cd(self):
        """_build_cmd 应包含 cd workspace"""
        backend = LocalDockerBackend(
            container_name="test-container", image="sandbox:latest", work_dir="workspace"
        )

        cmd = backend._build_cmd("echo hello")
        self.assertIn("cd", cmd)
        self.assertIn("workspace", cmd)
        self.assertIn("echo hello", cmd)

    def test_build_cmd_with_env_includes_cd(self):
        """_build_cmd_with_env 应包含 cd workspace"""
        backend = LocalDockerBackend(
            container_name="test-container", image="sandbox:latest", work_dir="workspace"
        )

        cmd = backend._build_cmd_with_env("echo hello", env={"KEY": "VALUE"})
        self.assertIn("cd", cmd)
        self.assertIn("workspace", cmd)
        self.assertIn("-e KEY=VALUE", cmd)


class TestRemoteDockerBackendWorkDir(unittest.TestCase):
    """RemoteDockerBackend 工作目录切换测试"""

    def test_build_cmd_includes_cd(self):
        """_build_cmd 应包含 cd workspace"""
        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteDockerBackend(
            container_name="test-container", ssh_config=ssh_config, work_dir="workspace"
        )

        cmd = backend._build_cmd("echo hello")
        self.assertIn("cd", cmd)
        self.assertIn("workspace", cmd)

    def test_build_cmd_with_env_includes_cd(self):
        """_build_cmd_with_env 应包含 cd workspace"""
        ssh_config = SSHConfig(host="test.example.com", user="test", password="test")
        backend = RemoteDockerBackend(
            container_name="test-container", ssh_config=ssh_config, work_dir="workspace"
        )

        cmd = backend._build_cmd_with_env("echo hello", env={"KEY": "VALUE"})
        self.assertIn("cd", cmd)
        self.assertIn("workspace", cmd)


class TestPathTraversalProtection(unittest.TestCase):
    """路径遍历防护测试"""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix="sandbox_test_")
        self.root_path = self.base_dir
        self.work_dir = "workspace"
        self.full_work_dir = os.path.join(self.base_dir, "workspace")
        os.makedirs(self.full_work_dir, exist_ok=True)
        self.backend = LocalSystemBackend(
            name="test", root_path=self.root_path, work_dir=self.work_dir
        )

    def tearDown(self):
        shutil.rmtree(self.base_dir, ignore_errors=True)

    def test_absolute_path_rejected(self):
        """绝对路径超出 work_dir 时应被拒绝"""
        with pytest.raises(ApiException, match="路径遍历被拒绝"):
            self.backend._validate_path("/etc/passwd")

    def test_dotdot_path_rejected(self):
        """../ 路径遍历应被拒绝"""
        with pytest.raises(ApiException, match="路径遍历被拒绝"):
            self.backend._validate_path("../../etc/passwd")

    def test_work_dir_path_allowed(self):
        """work_dir 内的路径应被允许"""
        result = self.backend._validate_path(f"{self.full_work_dir}/sub/file.txt")
        self.assertIsNotNone(result)

    def test_work_dir_exact_allowed(self):
        """work_dir 本身应被允许"""
        result = self.backend._validate_path(self.full_work_dir)
        self.assertIsNotNone(result)

    def test_write_validates_path(self):
        """write 应调用 _validate_path"""
        test_file = os.path.join(self.full_work_dir, "test.txt")
        result = self.backend.write(test_file, "hello")
        self.assertIsNone(result.error)

    def test_read_validates_path(self):
        """read 应调用 _validate_path"""
        test_file = os.path.join(self.full_work_dir, "test.txt")
        self.backend.write(test_file, "hello")
        content = self.backend.read(test_file)
        self.assertIn("hello", content)

    def test_edit_validates_path(self):
        """edit 应调用 _validate_path"""
        test_file = os.path.join(self.full_work_dir, "test.txt")
        self.backend.write(test_file, "hello world")
        result = self.backend.edit(test_file, "hello", "goodbye")
        self.assertIsNone(result.error)
        content = self.backend.read(test_file)
        self.assertIn("goodbye", content)

    def test_ls_validates_path(self):
        """ls 应调用 _validate_path"""
        # 使用虚拟路径（/ 表示 work_dir 根）
        result = self.backend.ls("/")
        self.assertIn("entries", result)

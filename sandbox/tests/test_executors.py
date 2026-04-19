"""执行器测试"""
import unittest

from sandbox.executors import execute_local, ExecResult, SSHConfig


class TestSubprocessExecutor(unittest.TestCase):
    def test_execute_local_success(self):
        result = execute_local("echo hello")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("hello", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_execute_local_failure(self):
        result = execute_local("ls /nonexistent_path_xyz")
        self.assertNotEqual(result.exit_code, 0)

    def test_execute_local_timeout(self):
        with self.assertRaises(Exception):
            execute_local("sleep 10", timeout=1)


class TestSSHConfig(unittest.TestCase):
    def test_ssh_config_defaults(self):
        config = SSHConfig(host="10.0.0.1")
        self.assertEqual(config.host, "10.0.0.1")
        self.assertEqual(config.port, 22)
        self.assertEqual(config.user, "")
        self.assertEqual(config.key_path, "")
        self.assertEqual(config.password, "")

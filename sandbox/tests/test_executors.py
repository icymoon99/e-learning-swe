"""执行器测试"""
import unittest

from sandbox.executors import execute_local, ExecResult, SSHConfig
from sandbox.executors.base import CLIExecutor, ExecutorRegistry, ExecutorResult


class MockExecutor(CLIExecutor):
    code = "mock"
    name = "Mock CLI"

    def build_command(self, query, session_id=None, **kwargs):
        return ["mock", "--query", query]

    def parse_output(self, raw_output):
        return ExecutorResult(success=True, session_id=None, output=raw_output)


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


class TestExecutorRegistry(unittest.TestCase):
    def setUp(self):
        self._prev = ExecutorRegistry._registry.copy()
        ExecutorRegistry._registry = {}

    def tearDown(self):
        ExecutorRegistry._registry = self._prev

    def test_register_and_get(self):
        ExecutorRegistry.register(MockExecutor())
        executor = ExecutorRegistry.get("mock")
        self.assertEqual(executor.code, "mock")
        self.assertEqual(executor.name, "Mock CLI")

    def test_get_unknown_raises(self):
        with self.assertRaises(KeyError):
            ExecutorRegistry.get("unknown")

    def test_list_all(self):
        ExecutorRegistry.register(MockExecutor())
        all_executors = ExecutorRegistry.list_all()
        self.assertEqual(len(all_executors), 1)
        self.assertIsInstance(all_executors[0], MockExecutor)

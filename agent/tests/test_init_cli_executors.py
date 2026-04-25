"""init_cli_executors 管理命令测试"""
import unittest
from django.core.management import call_command
from sandbox.executors.base import ExecutorRegistry


class TestInitCLIExecutors(unittest.TestCase):
    def setUp(self):
        self._prev = ExecutorRegistry._registry.copy()
        ExecutorRegistry._registry = {}

    def tearDown(self):
        ExecutorRegistry._registry = self._prev

    def test_register_trae_executor(self):
        call_command('init_cli_executors')
        executor = ExecutorRegistry.get('trae')
        self.assertEqual(executor.code, 'trae')
        self.assertEqual(executor.name, 'Trae CLI')

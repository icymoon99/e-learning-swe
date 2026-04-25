"""init_cli_executors 管理命令测试 — 写 DB 模式"""
import unittest
from django.core.management import call_command
from agent.models import ElExecutor


class TestInitCLIExecutors(unittest.TestCase):
    def setUp(self):
        # 清理已有数据
        ElExecutor.objects.all().delete()

    def test_inserts_trae_executor(self):
        call_command('init_cli_executors')
        ex = ElExecutor.objects.get(code='trae')
        self.assertEqual(ex.name, 'Trae CLI')
        self.assertEqual(ex.timeout, 3600)

    def test_idempotent(self):
        call_command('init_cli_executors')
        call_command('init_cli_executors')
        self.assertEqual(ElExecutor.objects.filter(code='trae').count(), 1)

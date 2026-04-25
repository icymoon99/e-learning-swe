"""ElExecutorConfig 模型测试"""
from django.test import TestCase
from agent.models import ElAgent, ElExecutorConfig


class TestElExecutorConfig(TestCase):
    def setUp(self):
        self.agent = ElAgent.objects.create(
            code='test_agent', name='Test', system_prompt='test'
        )

    def test_create_executor_config(self):
        config = ElExecutorConfig.objects.create(
            agent=self.agent, executor_code='trae', timeout=1800
        )
        self.assertTrue(config.enabled)
        self.assertEqual(config.timeout, 1800)
        self.assertEqual(str(config), 'test_agent -> trae')

    def test_unique_constraint(self):
        ElExecutorConfig.objects.create(
            agent=self.agent, executor_code='trae'
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ElExecutorConfig.objects.create(
                agent=self.agent, executor_code='trae'
            )

    def test_related_name_query(self):
        ElExecutorConfig.objects.create(
            agent=self.agent, executor_code='trae'
        )
        configs = self.agent.executor_configs.filter(enabled=True)
        self.assertEqual(configs.count(), 1)
        self.assertEqual(configs.first().executor_code, 'trae')

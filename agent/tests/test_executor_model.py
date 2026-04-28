from django.test import TestCase
from django.db import IntegrityError
from agent.models import ElAgent, ElExecutor
from sandbox.models import ElSandboxInstance


class TestElExecutor(TestCase):
    def test_create_executor(self):
        ex = ElExecutor.objects.create(
            code='trae', name='Trae CLI', timeout=3600
        )
        self.assertTrue(ex.enabled)
        self.assertEqual(ex.metadata, {})
        self.assertEqual(str(ex), 'Trae CLI (trae)')

    def test_unique_code(self):
        ElExecutor.objects.create(code='trae', name='Trae CLI')
        with self.assertRaises(IntegrityError):
            ElExecutor.objects.create(code='trae', name='Duplicate')

    def test_filter_enabled(self):
        ElExecutor.objects.create(code='trae', name='Trae CLI', enabled=True)
        ElExecutor.objects.create(code='other', name='Other', enabled=False)
        enabled = ElExecutor.objects.filter(enabled=True)
        self.assertEqual(enabled.count(), 1)
        self.assertEqual(enabled.first().code, 'trae')


class TestAgentExecutorFK(TestCase):
    def setUp(self):
        self.executor = ElExecutor.objects.create(
            code='trae', name='Trae CLI', timeout=1800
        )
        self.sandbox = ElSandboxInstance.objects.create(
            name='test-sandbox', type='local'
        )

    def test_agent_can_select_executor(self):
        agent = ElAgent.objects.create(
            code='test', name='Test', executor=self.executor, sandbox_instance=self.sandbox
        )
        self.assertEqual(agent.executor.code, 'trae')
        self.assertEqual(agent.executor.timeout, 1800)

    def test_agent_can_have_no_executor(self):
        agent = ElAgent.objects.create(code='test2', name='Test2', sandbox_instance=self.sandbox)
        self.assertIsNone(agent.executor)

    def test_executor_related_query(self):
        ElAgent.objects.create(code='a1', name='A1', executor=self.executor, sandbox_instance=self.sandbox)
        ElAgent.objects.create(code='a2', name='A2', executor=self.executor, sandbox_instance=self.sandbox)
        agents = self.executor.agents.all()
        self.assertEqual(agents.count(), 2)

"""Orchestrator CLI 集成测试 — FK 模式"""
import unittest
from unittest.mock import MagicMock, patch

from sandbox.executors.base import CLIExecutor, ExecutorRegistry, ExecutorResult
from agent.models import ElExecutor


class MockCLIExecutor(CLIExecutor):
    code = 'mock'
    name = 'Mock'

    def build_command(self, query, session_id=None, **kwargs):
        return ['mock', '--query', query]

    def parse_output(self, raw_output):
        return ExecutorResult(
            success=True, session_id='sid-1',
            output='ok', files_changed=[],
        )


class TestOrchestratorCLIIntegration(unittest.TestCase):
    def setUp(self):
        self._prev = ExecutorRegistry._registry.copy()
        ExecutorRegistry.register(MockCLIExecutor())

        # 创建 DB 执行器记录
        self.executor, _ = ElExecutor.objects.get_or_create(
            code='mock', defaults={'name': 'Mock', 'timeout': 3600}
        )

    def tearDown(self):
        ExecutorRegistry._registry = self._prev

    @patch('agent.orchestrator.ChatOpenAI')
    @patch('agent.orchestrator.resolve_backend')
    @patch('agent.orchestrator.ElAgent')
    @patch('agent.orchestrator.create_deep_agent')
    def test_build_agent_registers_code_workshop(
        self, mock_create, mock_el_agent, mock_resolve, mock_chat
    ):
        """验证 Orchestrator 通过 FK 获取执行器并注册 code_workshop tool"""
        agent_instance = MagicMock()
        agent_instance.code = 'test'
        agent_instance.llm_model = MagicMock()
        agent_instance.llm_model.model_code = 'gpt-4'
        agent_instance.llm_model.provider.resolved_base_url = 'https://api.openai.com'
        agent_instance.llm_model.provider.decrypted_api_key = 'sk-test'
        agent_instance.system_prompt = 'test'
        agent_instance.metadata = {}

        # FK 关联执行器
        agent_instance.executor = self.executor

        mock_el_agent.objects.get.return_value = agent_instance
        mock_resolve.return_value = MagicMock(execute=MagicMock())
        mock_chat.return_value = MagicMock()

        from agent.orchestrator import Orchestrator
        orch = Orchestrator()
        orch._agents = {}

        orch.get_or_create_agent('agent-id-1')

        call_kwargs = mock_create.call_args.kwargs
        self.assertIn('tools', call_kwargs)
        self.assertEqual(len(call_kwargs['tools']), 1)
        self.assertEqual(call_kwargs['tools'][0].name, 'code_workshop')

    @patch('agent.orchestrator.ChatOpenAI')
    @patch('agent.orchestrator.resolve_backend')
    @patch('agent.orchestrator.ElAgent')
    @patch('agent.orchestrator.create_deep_agent')
    def test_build_agent_without_executor(
        self, mock_create, mock_el_agent, mock_resolve, mock_chat
    ):
        """验证未配置执行器的 Agent 不调用 create_cli_tool"""
        agent_instance = MagicMock()
        agent_instance.code = 'test'
        agent_instance.llm_model = MagicMock()
        agent_instance.llm_model.model_code = 'gpt-4'
        agent_instance.llm_model.provider.resolved_base_url = 'https://api.openai.com'
        agent_instance.llm_model.provider.decrypted_api_key = 'sk-test'
        agent_instance.system_prompt = 'test'
        agent_instance.metadata = {}
        agent_instance.executor = None  # 无执行器

        mock_el_agent.objects.get.return_value = agent_instance
        mock_resolve.return_value = MagicMock(execute=MagicMock())
        mock_chat.return_value = MagicMock()

        from agent.orchestrator import Orchestrator
        orch = Orchestrator()
        orch._agents = {}

        orch.get_or_create_agent('agent-id-2')

        call_kwargs = mock_create.call_args.kwargs
        self.assertIn('tools', call_kwargs)
        self.assertEqual(len(call_kwargs['tools']), 0)

"""Orchestrator CLI 集成测试"""
import unittest
from unittest.mock import MagicMock, patch

from sandbox.executors.base import CLIExecutor, ExecutorRegistry, ExecutorResult


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

    def tearDown(self):
        ExecutorRegistry._registry = self._prev

    @patch('agent.orchestrator.ChatOpenAI')
    @patch('agent.orchestrator.resolve_backend')
    @patch('agent.orchestrator.ElAgent')
    @patch('agent.orchestrator.create_deep_agent')
    def test_build_agent_registers_code_workshop(
        self, mock_create, mock_el_agent, mock_resolve, mock_chat
    ):
        """验证 Orchestrator 为配置了执行器的 Agent 注册 code_workshop tool"""
        # 模拟 Agent 配置
        agent_instance = MagicMock()
        agent_instance.code = 'test'
        agent_instance.llm_model = MagicMock()
        agent_instance.llm_model.model_code = 'gpt-4'
        agent_instance.llm_model.provider.resolved_base_url = 'https://api.openai.com'
        agent_instance.llm_model.provider.decrypted_api_key = 'sk-test'
        agent_instance.system_prompt = 'test'
        agent_instance.metadata = {}

        # 模拟 executor_config
        exec_cfg = MagicMock()
        exec_cfg.executor_code = 'mock'
        exec_cfg.enabled = True
        exec_cfg.timeout = 3600
        agent_instance.executor_configs.filter.return_value = [exec_cfg]

        mock_el_agent.objects.get.return_value = agent_instance
        mock_resolve.return_value = MagicMock(execute=MagicMock())
        mock_chat.return_value = MagicMock()

        from agent.orchestrator import Orchestrator
        orch = Orchestrator()
        orch._agents = {}  # 清除缓存

        orch.get_or_create_agent('agent-id-1')

        # 验证 create_deep_agent 被调用且包含 tools
        call_kwargs = mock_create.call_args.kwargs
        self.assertIn('tools', call_kwargs)
        self.assertEqual(len(call_kwargs['tools']), 1)
        self.assertEqual(call_kwargs['tools'][0].name, 'code_workshop')

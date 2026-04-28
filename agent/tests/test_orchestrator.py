from unittest import mock
from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog, ElExecutor
from agent.orchestrator import Orchestrator
from llm.models import ElLLMProvider, ElLLMModel


class TestOrchestrator(TestCase):
    """Orchestrator 测试"""

    def setUp(self):
        self.provider = ElLLMProvider.objects.create(
            code="anthropic", name="Anthropic"
        )
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="claude-sonnet-4-6",
            display_name="Claude Sonnet 4.6",
        )
        self.agent = ElAgent.objects.create(
            code="test_agent",
            name="Test Agent",
            system_prompt="You are a test agent",
            llm_model=self.llm_model,
        )

    def test_get_or_create_agent_caches_instance(self):
        """验证 agent 实例被缓存，第二次调用不重新创建"""
        orchestrator = Orchestrator()
        with mock.patch.object(orchestrator, "_build_agent", return_value=mock.MagicMock()) as mock_build:
            result1 = orchestrator.get_or_create_agent(self.agent.id)
            result2 = orchestrator.get_or_create_agent(self.agent.id)
            self.assertIs(result1, result2)
            self.assertEqual(mock_build.call_count, 1)

    def test_get_or_create_agent_raises_on_not_found(self):
        """验证 agent 不存在时抛出异常"""
        orchestrator = Orchestrator()
        with self.assertRaises(Exception):
            orchestrator.get_or_create_agent("nonexistent-id")

    def test_execute_creates_execution_log(self):
        """验证执行时创建 ElAgentExecutionLog 记录"""
        orchestrator = Orchestrator()
        mock_agent = mock.MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "tool_call", "data": {"name": "test"}},
            {"type": "final_result", "data": {"answer": "done"}},
        ])
        with mock.patch.object(orchestrator, "get_or_create_agent", return_value=mock_agent):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="hello",
                thread_id="thread-test-001",
            )
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["execution_log_id"])
        log = ElAgentExecutionLog.objects.get(id=result["execution_log_id"])
        self.assertEqual(log.thread_id, "thread-test-001")
        self.assertEqual(len(log.events), 2)

    def test_execute_returns_result_data(self):
        """验证执行成功时返回 result 数据"""
        orchestrator = Orchestrator()
        mock_agent = mock.MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "final_result", "data": {"answer": "42"}},
        ])
        with mock.patch.object(orchestrator, "get_or_create_agent", return_value=mock_agent):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="what is the answer",
                thread_id="thread-result",
            )
        self.assertEqual(result["result"]["answer"], "42")

    def test_execute_handles_agent_error(self):
        """验证 agent 执行失败时正确记录错误"""
        orchestrator = Orchestrator()
        mock_agent = mock.MagicMock()
        mock_agent.stream.side_effect = Exception("LLM connection failed")
        with mock.patch.object(orchestrator, "get_or_create_agent", return_value=mock_agent):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="hello",
                thread_id="thread-test-002",
            )
        self.assertEqual(result["status"], "failed")
        self.assertIn("LLM connection failed", result["error_message"])
        log = ElAgentExecutionLog.objects.get(thread_id="thread-test-002")
        self.assertEqual(log.status, "failed")
        self.assertIn("LLM connection failed", log.error_message)

    def test_execute_with_empty_stream(self):
        """验证空事件流时 result 为最后一个事件"""
        orchestrator = Orchestrator()
        mock_agent = mock.MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "update", "data": {"intermediate": "step"}},
        ])
        with mock.patch.object(orchestrator, "get_or_create_agent", return_value=mock_agent):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="hello",
                thread_id="thread-empty",
            )
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["result"])

    def test_build_agent_creates_deep_agent(self):
        """验证 _build_agent 调用 create_deep_agent"""
        orchestrator = Orchestrator()
        with mock.patch("agent.orchestrator.resolve_backend") as mock_resolve, \
             mock.patch("agent.orchestrator.create_deep_agent") as mock_create:
            mock_create.return_value = mock.MagicMock()
            mock_llm_backend = mock.MagicMock()
            mock_resolve.return_value = mock_llm_backend
            with mock.patch("agent.orchestrator.ChatOpenAI") as mock_llm:
                mock_llm.return_value = mock.MagicMock()
                orchestrator._build_agent(self.agent.id)
                mock_create.assert_called_once()

    def test_build_agent_pass_env_vars_from_executor_metadata(self):
        """验证 _build_agent 从 executor.metadata 提取 env_vars 传递给 create_cli_tool"""
        executor = ElExecutor.objects.create(
            code="test_executor",
            name="Test Executor",
            metadata={"env_vars": {"API_KEY": "secret", "DEBUG": "true"}},
        )
        self.agent.executor = executor
        self.agent.save()

        orchestrator = Orchestrator()
        with mock.patch("agent.orchestrator.resolve_backend") as mock_resolve, \
             mock.patch("agent.orchestrator.create_deep_agent") as mock_create, \
             mock.patch("agent.orchestrator.ChatOpenAI") as mock_llm, \
             mock.patch("agent.orchestrator.create_cli_tool") as mock_cli_tool:
            mock_create.return_value = mock.MagicMock()
            mock_llm.return_value = mock.MagicMock()
            mock_cli_tool.return_value = mock.MagicMock()
            mock_resolve.return_value = mock.MagicMock()

            orchestrator._build_agent(self.agent.id)

            mock_cli_tool.assert_called_once()
            call_kwargs = mock_cli_tool.call_args[1]
            self.assertEqual(call_kwargs["env_vars"], {"API_KEY": "secret", "DEBUG": "true"})

    def test_build_agent_handles_empty_env_vars(self):
        """验证 executor.metadata 无 env_vars 时传递 None"""
        executor = ElExecutor.objects.create(
            code="test_executor2",
            name="Test Executor 2",
            metadata={"other_field": "value"},
        )
        self.agent.executor = executor
        self.agent.save()

        orchestrator = Orchestrator()
        with mock.patch("agent.orchestrator.resolve_backend") as mock_resolve, \
             mock.patch("agent.orchestrator.create_deep_agent") as mock_create, \
             mock.patch("agent.orchestrator.ChatOpenAI") as mock_llm, \
             mock.patch("agent.orchestrator.create_cli_tool") as mock_cli_tool:
            mock_create.return_value = mock.MagicMock()
            mock_llm.return_value = mock.MagicMock()
            mock_cli_tool.return_value = mock.MagicMock()
            mock_resolve.return_value = mock.MagicMock()

            orchestrator._build_agent(self.agent.id)

            mock_cli_tool.assert_called_once()
            call_kwargs = mock_cli_tool.call_args[1]
            self.assertIsNone(call_kwargs["env_vars"])

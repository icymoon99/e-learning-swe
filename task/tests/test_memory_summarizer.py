"""任务记忆摘要服务测试"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from llm.models import ElLLMModel, ElLLMProvider
from task.services.memory_summarizer import MemorySummarizer, estimate_tokens


class TestEstimateTokens(TestCase):
    """token 估算测试"""

    def test_chinese_text(self):
        """中文文本按 0.8 权重计算"""
        text = "测试内容" * 100
        result = estimate_tokens(text)
        self.assertGreater(result, 0)

    def test_empty_text(self):
        """空文本 token 为 0"""
        self.assertEqual(estimate_tokens(""), 0)


class TestMemorySummarizer(TestCase):
    """MemorySummarizer 测试"""

    def setUp(self):
        self.provider = ElLLMProvider.objects.create(
            code="openai",
            name="OpenAI",
            base_url="https://api.openai.com/v1/chat/completions",
        )
        self.provider.api_key_encrypted = "encrypted-sk-test123"
        self.provider.save(update_fields=["api_key_encrypted"])
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="gpt-4o-mini",
            display_name="GPT-4o Mini",
        )

    def test_summarizer_without_llm_model_truncates(self):
        """未传入 llm_model 时返回截断摘要"""
        summarizer = MemorySummarizer(token_limit=100)
        long_text = "测试内容" * 500
        result = summarizer.summarize(long_text)
        self.assertIn("[已截断", result)

    def test_summarizer_without_api_url_truncates(self):
        """provider 无 base_url 时返回截断摘要"""
        provider = ElLLMProvider.objects.create(
            code="empty",
            name="Empty",
        )
        llm_model = ElLLMModel.objects.create(
            provider=provider,
            model_code="test",
            display_name="Test",
        )
        summarizer = MemorySummarizer(token_limit=100, llm_model=llm_model)
        long_text = "测试内容" * 500
        result = summarizer.summarize(long_text)
        self.assertIn("[已截断", result)

    def test_summarizer_below_token_limit_returns_original(self):
        """未超过 token 限制时返回原文"""
        summarizer = MemorySummarizer(token_limit=9999, llm_model=self.llm_model)
        short_text = "简短测试内容"
        result = summarizer.summarize(short_text)
        self.assertEqual(result, short_text)

    @patch("task.services.memory_summarizer.httpx.post")
    def test_summarizer_calls_llm_on_success(self, mock_post):
        """LLM 调用成功时返回摘要"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "这是摘要"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock decrypted_api_key to return plain value
        with patch.object(
            type(self.provider),
            "decrypted_api_key",
            new_callable=lambda: property(lambda self: "sk-test123"),
        ):
            summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
            long_text = "测试内容" * 500
            result = summarizer.summarize(long_text)

        self.assertEqual(result, "这是摘要")
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs["json"]["model"], "gpt-4o-mini")
        self.assertIn("Bearer sk-test123", call_kwargs["headers"]["Authorization"])

    @patch("task.services.memory_summarizer.httpx.post")
    def test_summarizer_handles_empty_response(self, mock_post):
        """LLM 返回空内容时使用截断方案"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": ""}}]}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with patch.object(
            type(self.provider),
            "decrypted_api_key",
            new_callable=lambda: property(lambda self: "sk-test123"),
        ):
            summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
            long_text = "测试内容" * 500
            result = summarizer.summarize(long_text)

        self.assertIn("[已截断", result)

    @patch("task.services.memory_summarizer.httpx.post")
    def test_summarizer_handles_exception(self, mock_post):
        """LLM 调用异常时使用截断方案"""
        mock_post.side_effect = Exception("Network error")

        with patch.object(
            type(self.provider),
            "decrypted_api_key",
            new_callable=lambda: property(lambda self: "sk-test123"),
        ):
            summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
            long_text = "测试内容" * 500
            result = summarizer.summarize(long_text)

        self.assertIn("[已截断", result)


class TestTaskMemoryMiddlewareAgentLlm(TestCase):
    """测试 middleware 正确传入 agent LLM 配置到 summarizer"""

    def setUp(self):
        from agent.models import ElAgent
        from sandbox.models import ElSandboxInstance

        self.sandbox = ElSandboxInstance.objects.create(
            name="test", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        self.provider = ElLLMProvider.objects.create(
            code="anthropic", name="Anthropic",
            base_url="https://api.anthropic.com/v1/messages",
        )
        self.provider.api_key_encrypted = "encrypted-sk-ant"
        self.provider.save(update_fields=["api_key_encrypted"])
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="claude-sonnet-4-6",
            display_name="Claude Sonnet 4.6",
        )

        # Mock decrypted_api_key on the provider class
        self._decrypted_key_patcher = patch.object(
            type(self.provider),
            "decrypted_api_key",
            new_callable=lambda: property(lambda self: "sk-ant-test"),
        )
        self._decrypted_key_patcher.start()

        self.agent = ElAgent.objects.create(
            code="test_agent",
            name="Test Agent",
            system_prompt="Test",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )

    def tearDown(self):
        self._decrypted_key_patcher.stop()

    def test_middleware_uses_agent_llm_model(self):
        """middleware 使用 agent 的 LLM 模型创建 summarizer"""
        from task.middleware.task_memory import TaskMemoryMiddleware

        middleware = TaskMemoryMiddleware(task_id="task-1", agent_code="test_agent")
        self.assertIsNotNone(middleware.summarizer.llm_model)
        self.assertEqual(middleware.summarizer.llm_model.model_code, "claude-sonnet-4-6")

    def test_middleware_without_agent_code_uses_no_llm(self):
        """不传 agent_code 时 summarizer 无 LLM 模型"""
        from task.middleware.task_memory import TaskMemoryMiddleware

        middleware = TaskMemoryMiddleware(task_id="task-1")
        self.assertIsNone(middleware.summarizer.llm_model)

    def test_middleware_with_nonexistent_agent_code(self):
        """传入不存在的 agent_code 时使用默认摘要服务"""
        from task.middleware.task_memory import TaskMemoryMiddleware

        middleware = TaskMemoryMiddleware(task_id="task-1", agent_code="nonexistent")
        self.assertIsNone(middleware.summarizer.llm_model)

    def test_middleware_with_agent_without_llm_model(self):
        """agent 无 llm_model 时使用默认摘要服务"""
        from agent.models import ElAgent
        from sandbox.models import ElSandboxInstance
        from task.middleware.task_memory import TaskMemoryMiddleware

        sandbox = ElSandboxInstance.objects.create(
            name="test2", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        agent_no_llm = ElAgent.objects.create(
            code="agent_no_llm",
            name="Agent No LLM",
            system_prompt="Test",
            sandbox_instance=sandbox,
        )
        middleware = TaskMemoryMiddleware(task_id="task-1", agent_code="agent_no_llm")
        self.assertIsNone(middleware.summarizer.llm_model)

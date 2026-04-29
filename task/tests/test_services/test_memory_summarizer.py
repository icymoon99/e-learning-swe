"""任务记忆摘要服务测试（旧版 settings 配置方式，已迁移至 llm_model）"""

from unittest.mock import patch, MagicMock

from django.test import TestCase

from llm.models import ElLLMModel, ElLLMProvider
from task.services.memory_summarizer import (
    MemorySummarizer,
    estimate_tokens,
    SUMMARY_TOKEN_LIMIT,
)


class EstimateTokensTest(TestCase):
    def test_chinese_only(self):
        """纯中文 token 估算"""
        text = "这是一个测试"
        tokens = estimate_tokens(text)
        self.assertEqual(tokens, int(6 * 0.8))

    def test_english_only(self):
        """纯英文 token 估算"""
        text = "hello world"
        tokens = estimate_tokens(text)
        self.assertEqual(tokens, int(11 * 0.25))

    def test_mixed(self):
        """混合中英文"""
        text = "hello 你好"
        tokens = estimate_tokens(text)
        expected = int(6 * 0.25 + 2 * 0.8)
        self.assertEqual(tokens, expected)


class MemorySummarizerTest(TestCase):
    """MemorySummarizer 测试（使用 llm_model 参数）"""

    def setUp(self):
        self.provider = ElLLMProvider.objects.create(
            code="openai",
            name="OpenAI",
            base_url="https://api.example.com/v1/chat/completions",
        )
        self.provider.api_key_encrypted = "encrypted-test-key"
        self.provider.save(update_fields=["api_key_encrypted"])
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="gpt-4o-mini",
            display_name="GPT-4o Mini",
        )
        # Mock decrypted_api_key
        self._key_patcher = patch.object(
            type(self.provider),
            "decrypted_api_key",
            new_callable=lambda: property(lambda self: "test-key"),
        )
        self._key_patcher.start()

    def tearDown(self):
        self._key_patcher.stop()

    def test_needs_summary_false_for_short_text(self):
        """短文本不需要摘要"""
        summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
        text = "这是一段短文本"
        self.assertFalse(summarizer.needs_summary(text))

    def test_needs_summary_true_for_long_text(self):
        """长文本需要摘要"""
        summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
        text = "这是一段很长的文本" * 50
        self.assertTrue(summarizer.needs_summary(text))

    def test_summarize_returns_text_as_is_when_short(self):
        """短文本直接返回"""
        summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
        text = "短文本内容"
        result = summarizer.summarize(text)
        self.assertEqual(result, text)

    @patch("task.services.memory_summarizer.httpx.post")
    def test_summarize_calls_llm_for_long_text(self, mock_post):
        """长文本调用 LLM 摘要"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "摘要结果"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
        long_text = "详细内容" * 100
        result = summarizer.summarize(long_text)

        self.assertEqual(result, "摘要结果")
        mock_post.assert_called_once()

    @patch("task.services.memory_summarizer.httpx.post")
    def test_summarize_falls_back_to_truncate_on_llm_failure(self, mock_post):
        """LLM 调用失败时降级为截断"""
        mock_post.side_effect = Exception("API 错误")

        summarizer = MemorySummarizer(token_limit=100, llm_model=self.llm_model)
        long_text = "详细内容" * 100
        result = summarizer.summarize(long_text)

        self.assertIn("已截断", result)

    def test_summarize_falls_back_when_no_llm_model(self):
        """无 llm_model 时降级为截断"""
        summarizer = MemorySummarizer(token_limit=100)
        long_text = "详细内容" * 100
        result = summarizer.summarize(long_text)
        self.assertIn("已截断", result)

    def test_summarize_falls_back_when_provider_has_no_base_url(self):
        """provider 无 base_url 时降级为截断"""
        provider = ElLLMProvider.objects.create(code="no-url", name="No URL")
        llm_model = ElLLMModel.objects.create(
            provider=provider,
            model_code="test",
            display_name="Test",
        )
        summarizer = MemorySummarizer(token_limit=100, llm_model=llm_model)
        long_text = "详细内容" * 100
        result = summarizer.summarize(long_text)
        self.assertIn("已截断", result)

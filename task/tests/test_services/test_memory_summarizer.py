from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings

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
        # english: 6 chars (hello + space) × 0.25 = 1.5 → 1
        # chinese: 2 × 0.8 = 1.6 → 1
        tokens = estimate_tokens(text)
        expected = int(6 * 0.25 + 2 * 0.8)
        self.assertEqual(tokens, expected)


class MemorySummarizerTest(TestCase):
    def setUp(self):
        self.summarizer = MemorySummarizer(
            token_limit=100,
            api_url="https://api.example.com/v1/chat/completions",
            api_key="test-key",
        )

    def test_needs_summary_false_for_short_text(self):
        """短文本不需要摘要"""
        text = "这是一段短文本"
        self.assertFalse(self.summarizer.needs_summary(text))

    def test_needs_summary_true_for_long_text(self):
        """长文本需要摘要"""
        text = "这是一段很长的文本" * 50
        self.assertTrue(self.summarizer.needs_summary(text))

    def test_summarize_returns_text_as_is_when_short(self):
        """短文本直接返回"""
        text = "短文本内容"
        result = self.summarizer.summarize(text)
        self.assertEqual(result, text)

    @patch("httpx.post")
    def test_summarize_calls_llm_for_long_text(self, mock_post):
        """长文本调用 LLM 摘要"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "摘要结果"}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        long_text = "详细内容" * 100
        result = self.summarizer.summarize(long_text)

        self.assertEqual(result, "摘要结果")
        mock_post.assert_called_once()

    @patch("httpx.post")
    def test_summarize_falls_back_to_truncate_on_llm_failure(self, mock_post):
        """LLM 调用失败时降级为截断"""
        mock_post.side_effect = Exception("API 错误")

        long_text = "详细内容" * 100
        result = self.summarizer.summarize(long_text)

        self.assertIn("已截断", result)

    def test_summarize_falls_back_when_no_api_config(self):
        """无 API 配置时降级为截断"""
        summarizer = MemorySummarizer(token_limit=100, api_url="", api_key="")
        long_text = "详细内容" * 100
        result = summarizer.summarize(long_text)
        self.assertIn("已截断", result)

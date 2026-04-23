"""任务记忆摘要服务"""
import logging
from typing import Optional

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

# Token 估算权重
CHINESE_CHAR_WEIGHT = 0.8
OTHER_CHAR_WEIGHT = 0.25

# 摘要 Token 上限
SUMMARY_TOKEN_LIMIT = 8000


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量

    中文字符 × 0.8 + 其他字符 × 0.25
    """
    chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    other_count = len(text) - chinese_count
    return int(chinese_count * CHINESE_CHAR_WEIGHT + other_count * OTHER_CHAR_WEIGHT)


class MemorySummarizer:
    """记忆摘要服务

    当记忆内容超过 Token 限制时，使用轻量级 LLM 进行摘要。
    """

    def __init__(
        self,
        token_limit: int = SUMMARY_TOKEN_LIMIT,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "qwen-turbo",
    ):
        self.token_limit = token_limit
        self.api_url = api_url or getattr(settings, "LLM_SUMMARY_API_URL", "")
        self.api_key = api_key or getattr(settings, "LLM_SUMMARY_API_KEY", "")
        self.model = model

    def needs_summary(self, text: str) -> bool:
        """判断是否需要摘要"""
        return estimate_tokens(text) > self.token_limit

    def summarize(self, text: str) -> str:
        """对文本进行摘要

        如果文本未超过 token 限制，直接返回原文。
        超过限制时调用 LLM 进行摘要。
        """
        if not self.needs_summary(text):
            return text

        if not self.api_url or not self.api_key:
            logger.warning(
                "LLM_SUMMARY_API_URL 或 LLM_SUMMARY_API_KEY 未配置，"
                "返回截断摘要而非 LLM 摘要"
            )
            return self._truncate_summary(text)

        return self._llm_summarize(text)

    def _truncate_summary(self, text: str) -> str:
        """截断摘要（LLM 不可用时的降级方案）"""
        max_chars = int(self.token_limit / CHINESE_CHAR_WEIGHT)
        truncated = text[:max_chars]
        return f"{truncated}...[已截断，超出 {self.token_limit} token 限制]"

    def _llm_summarize(self, text: str) -> str:
        """调用 LLM 进行智能摘要"""
        try:
            response = httpx.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "你是一个代码项目记忆的摘要助手。"
                                "请将以下内容精简为关键要点，保留重要的技术决策、"
                                "代码变更和问题解决信息。使用中文回复。"
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"请摘要以下内容：\n\n{text}",
                        },
                    ],
                    "max_tokens": 2000,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            summary = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not summary:
                logger.warning("LLM 返回空摘要，使用截断方案")
                return self._truncate_summary(text)
            return summary
        except Exception as e:
            logger.error(f"LLM 摘要调用失败: {e}，使用截断方案")
            return self._truncate_summary(text)

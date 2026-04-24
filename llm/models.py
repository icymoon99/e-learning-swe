from django.db import models
from core.models import AbstractBaseModel


class ElLLMProvider(AbstractBaseModel):
    """LLM 供应商配置"""

    code = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="供应商编码")
    name = models.CharField(max_length=128, verbose_name="供应商名称")
    base_url = models.CharField(max_length=512, default="", verbose_name="API 基础地址")
    api_key_encrypted = models.TextField(default="", verbose_name="API 密钥（加密）")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    description = models.TextField(default="", blank=True, verbose_name="描述")

    class Meta:
        db_table = "el_llm_provider"
        verbose_name = "LLM 供应商"
        verbose_name_plural = verbose_name
        # Override AbstractBaseModel's ordering
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def resolved_base_url(self) -> str:
        """解析 base_url：预置供应商从常量获取，自定义供应商从数据库读取"""
        from llm.constants import PRESET_PROVIDERS
        if self.code in PRESET_PROVIDERS:
            return PRESET_PROVIDERS[self.code]["base_url"]
        return self.base_url

    @property
    def decrypted_api_key(self) -> str:
        """解密 API 密钥"""
        from core.common.utils.aes_utils import aes_decrypt
        if not self.api_key_encrypted:
            return ""
        return aes_decrypt(self.api_key_encrypted)


class ElLLMModel(AbstractBaseModel):
    """LLM 模型定义"""

    provider = models.ForeignKey(
        ElLLMProvider, on_delete=models.CASCADE,
        related_name="models", verbose_name="所属供应商"
    )
    model_code = models.CharField(max_length=128, verbose_name="模型编码")
    display_name = models.CharField(max_length=255, default="", verbose_name="显示名称")
    context_window = models.IntegerField(default=0, verbose_name="上下文窗口（tokens）")
    max_output_tokens = models.IntegerField(default=0, verbose_name="最大输出 tokens")
    enabled = models.BooleanField(default=True, verbose_name="是否可用")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    description = models.TextField(default="", blank=True, verbose_name="描述")

    class Meta:
        db_table = "el_llm_model"
        verbose_name = "LLM 模型"
        verbose_name_plural = verbose_name
        unique_together = [["provider", "model_code"]]
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.model_code})"

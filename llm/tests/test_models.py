from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from llm.models import ElLLMProvider, ElLLMModel
from llm.constants import PRESET_PROVIDERS


class ElLLMProviderModelTest(TestCase):
    """ElLLMProvider 模型单元测试"""

    def test_resolved_base_url_returns_constant_for_preset(self):
        """预置供应商的 resolved_base_url 返回常量值"""
        provider = ElLLMProvider.objects.create(
            code="openai",
            name="OpenAI",
            base_url="",  # 数据库存空
        )
        expected = PRESET_PROVIDERS["openai"]["base_url"]
        self.assertEqual(provider.resolved_base_url, expected)

    def test_resolved_base_url_returns_db_value_for_custom(self):
        """自定义供应商的 resolved_base_url 返回数据库值"""
        custom_url = "http://192.168.1.100:8000/v1"
        provider = ElLLMProvider.objects.create(
            code="local_vllm",
            name="本地 vLLM",
            base_url=custom_url,
        )
        self.assertEqual(provider.resolved_base_url, custom_url)

    def test_resolved_base_url_empty_for_custom_without_url(self):
        """自定义供应商未设置 base_url 时返回空字符串"""
        provider = ElLLMProvider.objects.create(
            code="empty_custom",
            name="空自定义",
            base_url="",
        )
        self.assertEqual(provider.resolved_base_url, "")

    def test_str_representation(self):
        """__str__ 返回 名称 (编码)"""
        provider = ElLLMProvider.objects.create(
            code="anthropic",
            name="Anthropic",
        )
        self.assertEqual(str(provider), "Anthropic (anthropic)")

    @patch("core.common.utils.aes_utils.aes_decrypt")
    def test_decrypted_api_key_calls_decrypt(self, mock_decrypt):
        """decrypted_api_key 属性调用 aes_utils.aes_decrypt"""
        mock_decrypt.return_value = "sk-test-key"
        provider = ElLLMProvider.objects.create(
            code="test_provider",
            name="Test",
            api_key_encrypted="encrypted_value",
        )
        result = provider.decrypted_api_key
        mock_decrypt.assert_called_once_with("encrypted_value")
        self.assertEqual(result, "sk-test-key")

    @patch("core.common.utils.aes_utils.aes_decrypt")
    def test_decrypted_api_key_empty_when_no_encrypted_value(self, mock_decrypt):
        """api_key_encrypted 为空时 decrypted_api_key 返回空字符串"""
        provider = ElLLMProvider.objects.create(
            code="test_no_key",
            name="Test No Key",
            api_key_encrypted="",
        )
        result = provider.decrypted_api_key
        mock_decrypt.assert_not_called()
        self.assertEqual(result, "")


class ElLLMModelModelTest(TestCase):
    """ElLLMModel 模型单元测试"""

    def setUp(self):
        self.provider = ElLLMProvider.objects.create(
            code="openai", name="OpenAI"
        )

    def test_unique_together_provider_and_model_code(self):
        """同一供应商下 model_code 唯一"""
        ElLLMModel.objects.create(
            provider=self.provider, model_code="gpt-4o", display_name="GPT-4o"
        )
        with self.assertRaises(IntegrityError):
            ElLLMModel.objects.create(
                provider=self.provider, model_code="gpt-4o", display_name="Duplicate"
            )

    def test_different_providers_can_have_same_model_code(self):
        """不同供应商可以有相同的 model_code"""
        provider2 = ElLLMProvider.objects.create(
            code="another", name="Another"
        )
        ElLLMModel.objects.create(
            provider=self.provider, model_code="custom-model", display_name="Model A"
        )
        ElLLMModel.objects.create(
            provider=provider2, model_code="custom-model", display_name="Model B"
        )
        self.assertEqual(ElLLMModel.objects.count(), 2)

    def test_str_representation(self):
        """__str__ 返回 display_name (model_code)"""
        model = ElLLMModel.objects.create(
            provider=self.provider, model_code="gpt-4o", display_name="GPT-4o"
        )
        self.assertEqual(str(model), "GPT-4o (gpt-4o)")

    def test_default_ordering(self):
        """模型按 sort_order 和 id 排序"""
        m1 = ElLLMModel.objects.create(
            provider=self.provider, model_code="m1", display_name="M1", sort_order=10
        )
        m2 = ElLLMModel.objects.create(
            provider=self.provider, model_code="m2", display_name="M2", sort_order=1
        )
        models = list(ElLLMModel.objects.all())
        self.assertEqual(models[0], m2)
        self.assertEqual(models[1], m1)

    def test_cascade_delete_provider_deletes_models(self):
        """删除供应商时，关联的模型级联删除"""
        model = ElLLMModel.objects.create(
            provider=self.provider, model_code="gpt-4o", display_name="GPT-4o"
        )
        self.provider.delete()
        self.assertFalse(ElLLMModel.objects.filter(id=model.id).exists())

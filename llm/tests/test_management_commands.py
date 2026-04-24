from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from llm.models import ElLLMProvider, ElLLMModel
from llm.constants import PRESET_PROVIDERS


class InitLLMProvidersCommandTest(TestCase):
    """init_llm_providers 管理命令测试"""

    def _run_command(self, *args, **kwargs):
        out = StringIO()
        err = StringIO()
        call_command("init_llm_providers", *args, stdout=out, stderr=err, **kwargs)
        return out.getvalue(), err.getvalue()

    def test_creates_all_preset_providers(self):
        """首次运行时创建所有预置供应商"""
        self.assertEqual(ElLLMProvider.objects.count(), 0)
        out, err = self._run_command()
        self.assertEqual(ElLLMProvider.objects.count(), len(PRESET_PROVIDERS))
        for code in PRESET_PROVIDERS:
            self.assertTrue(ElLLMProvider.objects.filter(code=code).exists())

    def test_creates_models_for_each_provider(self):
        """为每个预置供应商创建对应的模型"""
        self._run_command()
        for code, data in PRESET_PROVIDERS.items():
            provider = ElLLMProvider.objects.get(code=code)
            expected_model_count = len(data["models"])
            actual_model_count = ElLLMModel.objects.filter(provider=provider).count()
            self.assertEqual(actual_model_count, expected_model_count, f"Provider {code} should have {expected_model_count} models")

    def test_idempotent_no_duplicate_creation(self):
        """幂等：重复运行不会创建重复数据"""
        self._run_command()
        provider_count = ElLLMProvider.objects.count()
        model_count = ElLLMModel.objects.count()
        out, err = self._run_command()
        self.assertEqual(ElLLMProvider.objects.count(), provider_count)
        self.assertEqual(ElLLMModel.objects.count(), model_count)

    def test_skips_existing_providers(self):
        """跳过已存在的供应商，输出跳过提示"""
        ElLLMProvider.objects.create(code="openai", name="OpenAI")
        out, _ = self._run_command()
        self.assertIn("跳过", out)
        # openai 已存在，其他供应商仍应被创建
        self.assertEqual(ElLLMProvider.objects.count(), len(PRESET_PROVIDERS))

    def test_force_updates_existing_provider_name(self):
        """--force 更新已存在供应商的名称"""
        ElLLMProvider.objects.create(code="openai", name="旧名称")
        out, _ = self._run_command(force=True)
        provider = ElLLMProvider.objects.get(code="openai")
        self.assertEqual(provider.name, PRESET_PROVIDERS["openai"]["name"])
        self.assertIn("更新", out)

    def test_force_updates_existing_model_fields(self):
        """--force 更新已存在模型的字段"""
        provider = ElLLMProvider.objects.create(code="openai", name="OpenAI")
        model = ElLLMModel.objects.create(
            provider=provider,
            model_code="gpt-4.1",
            display_name="旧名称",
            context_window=1000,
            max_output_tokens=1000,
        )
        out, _ = self._run_command(force=True)
        model.refresh_from_db()
        preset_model = PRESET_PROVIDERS["openai"]["models"][0]
        self.assertEqual(model.display_name, preset_model["display_name"])
        self.assertEqual(model.context_window, preset_model["context_window"])
        self.assertEqual(model.max_output_tokens, preset_model["max_output_tokens"])

    def test_does_not_modify_custom_providers(self):
        """不修改用户自定义的供应商（不在 PRESET_PROVIDERS 中的）"""
        custom = ElLLMProvider.objects.create(
            code="my_custom_provider",
            name="我的自定义",
            base_url="http://custom.local/v1",
        )
        self._run_command()
        custom.refresh_from_db()
        self.assertEqual(custom.name, "我的自定义")
        self.assertEqual(custom.base_url, "http://custom.local/v1")

    def test_output_summary(self):
        """输出创建/跳过的统计摘要"""
        out, _ = self._run_command()
        self.assertIn("创建", out)
        self.assertIn("模型", out)

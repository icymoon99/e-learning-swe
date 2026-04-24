from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from llm.models import ElLLMProvider, ElLLMModel

ElUser = get_user_model()


class TestElLLMProviderViewSet(APITestCase):
    """LLM 供应商 ViewSet API 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = ElUser.objects.create_user(
            username="testadmin", password="testpass123", is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.provider = ElLLMProvider.objects.create(
            code="openai", name="OpenAI", enabled=True
        )

    def test_list_providers(self):
        """测试列表接口"""
        resp = self.client.get("/api/llm/providers/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["content"]["results"]), 1)

    def test_retrieve_provider(self):
        """测试详情接口"""
        resp = self.client.get(f"/api/llm/providers/{self.provider.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["code"], "openai")

    def test_create_provider(self):
        """测试创建接口（管理员）"""
        data = {
            "code": "anthropic",
            "name": "Anthropic",
            "base_url": "https://api.anthropic.com/v1",
            "api_key_encrypted": "encrypted-key",
        }
        resp = self.client.post("/api/llm/providers/", data, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        self.assertEqual(ElLLMProvider.objects.count(), 2)

    def test_update_provider(self):
        """测试更新接口"""
        resp = self.client.patch(
            f"/api/llm/providers/{self.provider.id}/",
            {"name": "OpenAI Updated"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.json())
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.name, "OpenAI Updated")

    def test_delete_provider(self):
        """测试删除接口"""
        resp = self.client.delete(f"/api/llm/providers/{self.provider.id}/")
        self.assertEqual(resp.status_code, 200, resp.json())
        self.assertFalse(ElLLMProvider.objects.filter(id=self.provider.id).exists())

    def test_filter_by_enabled(self):
        """测试按 enabled 过滤"""
        ElLLMProvider.objects.create(code="disabled", name="Disabled", enabled=False)
        resp = self.client.get("/api/llm/providers/", {"enabled": "true"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["count"], 1)


class TestElLLMModelViewSet(APITestCase):
    """LLM 模型 ViewSet API 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = ElUser.objects.create_user(
            username="testadmin", password="testpass123", is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.provider = ElLLMProvider.objects.create(
            code="openai", name="OpenAI"
        )
        self.model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="gpt-4o",
            display_name="GPT-4o",
            enabled=True,
        )

    def test_list_models(self):
        """测试列表接口"""
        resp = self.client.get("/api/llm/models/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["content"]["results"]), 1)

    def test_retrieve_model(self):
        """测试详情接口"""
        resp = self.client.get(f"/api/llm/models/{self.model.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["model_code"], "gpt-4o")

    def test_create_model(self):
        """测试创建接口"""
        data = {
            "provider": self.provider.id,
            "model_code": "gpt-4o-mini",
            "display_name": "GPT-4o Mini",
        }
        resp = self.client.post("/api/llm/models/", data, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        self.assertEqual(ElLLMModel.objects.count(), 2)

    def test_update_model(self):
        """测试更新接口"""
        resp = self.client.patch(
            f"/api/llm/models/{self.model.id}/",
            {"display_name": "Updated GPT-4o"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.json())
        self.model.refresh_from_db()
        self.assertEqual(self.model.display_name, "Updated GPT-4o")

    def test_delete_model(self):
        """测试删除接口"""
        resp = self.client.delete(f"/api/llm/models/{self.model.id}/")
        self.assertEqual(resp.status_code, 200, resp.json())
        self.assertFalse(ElLLMModel.objects.filter(id=self.model.id).exists())

    def test_dropdown_returns_enabled_models(self):
        """测试下拉接口只返回启用的模型"""
        ElLLMModel.objects.create(
            provider=self.provider,
            model_code="disabled-model",
            display_name="Disabled",
            enabled=False,
        )
        resp = self.client.get("/api/llm/models/dropdown/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # 只返回 enabled=True 的模型
        codes = [m["model_code"] for m in data["content"]]
        self.assertIn("gpt-4o", codes)
        self.assertNotIn("disabled-model", codes)

    def test_dropdown_includes_provider_info(self):
        """测试下拉接口包含供应商信息"""
        resp = self.client.get("/api/llm/models/dropdown/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        model = data["content"][0]
        self.assertEqual(model["provider_name"], "OpenAI")
        self.assertEqual(model["provider_code"], "openai")

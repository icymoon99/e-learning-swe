"""视图 CRUD 测试"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from sandbox.models import ElSandboxInstance
from agent.models import ElAgent
from llm.models import ElLLMProvider, ElLLMModel


User = get_user_model()


class SandboxInstanceCRUDTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_localdocker(self):
        data = {
            "name": "create-test",
            "type": "localdocker",
            "metadata": {"image": "sandbox:latest", "work_dir": "/workspace"},
        }
        resp = self.client.post("/api/sandbox/instances/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["content"]["name"], "create-test")

    def test_create_remotesystem_requires_ssh_host(self):
        data = {
            "name": "remote-bad",
            "type": "remotesystem",
            "metadata": {"work_dir": "/home/sandbox"},
        }
        resp = self.client.post("/api/sandbox/instances/", data, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_list_instances(self):
        ElSandboxInstance.objects.create(
            name="list-1", type="localsystem"
        )
        ElSandboxInstance.objects.create(
            name="list-2", type="localdocker"
        )
        resp = self.client.get("/api/sandbox/instances/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["count"], 2)

    def test_retrieve_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="get-test", type="localsystem"
        )
        resp = self.client.get(f"/api/sandbox/instances/{instance.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["name"], "get-test")

    def test_update_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="old", type="localsystem"
        )
        resp = self.client.patch(
            f"/api/sandbox/instances/{instance.id}/",
            {"name": "new"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        instance.refresh_from_db()
        self.assertEqual(instance.name, "new")

    def test_delete_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="delete-me", type="localsystem"
        )
        resp = self.client.delete(f"/api/sandbox/instances/{instance.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ElSandboxInstance.objects.filter(id=instance.id).exists())

    def test_execute_missing_command(self):
        instance = ElSandboxInstance.objects.create(
            name="exec-bad", type="localsystem"
        )
        resp = self.client.post(
            f"/api/sandbox/instances/{instance.id}/execute/", {}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("command", resp.data.get("message", ""))

    def test_execute_localsystem(self):
        instance = ElSandboxInstance.objects.create(
            name="exec-good", type="localsystem",
            metadata={"work_dir": "/tmp"},
        )
        resp = self.client.post(
            f"/api/sandbox/instances/{instance.id}/execute/",
            {"command": "echo hello"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("hello", resp.data["content"]["output"])

    def test_start_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="start-test", type="localsystem",
            metadata={"work_dir": "/tmp/sandbox-start-test"},
        )
        resp = self.client.post(f"/api/sandbox/instances/{instance.id}/start/")
        self.assertEqual(resp.status_code, 200)
        instance.refresh_from_db()
        self.assertEqual(instance.status, "active")

    def test_reset_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="reset-api", type="localsystem",
            metadata={"work_dir": "/tmp/sandbox-reset-test"},
        )
        resp = self.client.post(f"/api/sandbox/instances/{instance.id}/reset/")
        self.assertEqual(resp.status_code, 200)

    def test_types_action(self):
        """GET /api/sandbox/instances/types/ 返回所有类型和 schema"""
        resp = self.client.get("/api/sandbox/instances/types/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("types", resp.data["content"])
        types = resp.data["content"]["types"]
        self.assertEqual(len(types), 4)
        self.assertIn("localdocker", types)
        self.assertIn("localsystem", types)
        # 验证每种类型都有 label 和 fields
        for type_name, type_schema in types.items():
            self.assertIn("label", type_schema)
            self.assertIn("fields", type_schema)

    def test_delete_sandbox_with_bound_agent_fails(self):
        """有 Agent 绑定的沙箱不能删除"""
        provider = ElLLMProvider.objects.create(code="test", name="Test")
        llm = ElLLMModel.objects.create(
            provider=provider, model_code="test-model", display_name="Test"
        )
        instance = ElSandboxInstance.objects.create(
            name="bound-sandbox", type="localsystem",
            metadata={"work_dir": "/tmp"},
        )
        ElAgent.objects.create(
            code="bound-agent", name="Bound Agent",
            llm_model=llm, sandbox_instance=instance,
        )

        resp = self.client.delete(f"/api/sandbox/instances/{instance.id}/")
        data = resp.json()
        self.assertIn("绑定", data.get("message", ""))
        # 沙箱应仍然存在
        self.assertTrue(ElSandboxInstance.objects.filter(id=instance.id).exists())

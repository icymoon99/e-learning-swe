"""视图 CRUD 测试"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from sandbox.models import ElSandboxInstance


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
            "root_path": "/workspace",
            "metadata": {"image": "sandbox:latest", "work_dir": "/workspace"},
        }
        resp = self.client.post("/api/sandbox/instances/", data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["content"]["name"], "create-test")

    def test_create_remotesystem_requires_ssh_host(self):
        data = {
            "name": "remote-bad",
            "type": "remotesystem",
            "root_path": "/home/sandbox",
            "metadata": {"work_dir": "/home/sandbox"},
        }
        resp = self.client.post("/api/sandbox/instances/", data, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_list_instances(self):
        ElSandboxInstance.objects.create(
            name="list-1", type="localsystem", root_path="/test"
        )
        ElSandboxInstance.objects.create(
            name="list-2", type="localdocker", root_path="/test"
        )
        resp = self.client.get("/api/sandbox/instances/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["count"], 2)

    def test_retrieve_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="get-test", type="localsystem", root_path="/test"
        )
        resp = self.client.get(f"/api/sandbox/instances/{instance.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["name"], "get-test")

    def test_update_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="old", type="localsystem", root_path="/test"
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
            name="delete-me", type="localsystem", root_path="/test"
        )
        resp = self.client.delete(f"/api/sandbox/instances/{instance.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ElSandboxInstance.objects.filter(id=instance.id).exists())

    def test_execute_missing_command(self):
        instance = ElSandboxInstance.objects.create(
            name="exec-bad", type="localsystem", root_path="/tmp"
        )
        resp = self.client.post(
            f"/api/sandbox/instances/{instance.id}/execute/", {}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("command", resp.data.get("message", ""))

    def test_execute_localsystem(self):
        instance = ElSandboxInstance.objects.create(
            name="exec-good", type="localsystem", root_path="/tmp"
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
            name="start-test", type="localsystem", root_path="/tmp"
        )
        resp = self.client.post(f"/api/sandbox/instances/{instance.id}/start/")
        self.assertEqual(resp.status_code, 200)
        instance.refresh_from_db()
        self.assertEqual(instance.status, "active")

    def test_reset_instance(self):
        instance = ElSandboxInstance.objects.create(
            name="reset-api", type="localsystem", root_path="/tmp"
        )
        resp = self.client.post(f"/api/sandbox/instances/{instance.id}/reset/")
        self.assertEqual(resp.status_code, 200)

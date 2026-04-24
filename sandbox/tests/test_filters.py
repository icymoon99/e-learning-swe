"""过滤器测试"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from sandbox.models import ElSandboxInstance


User = get_user_model()


class TestSandboxInstanceFilter(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        ElSandboxInstance.objects.create(
            name="docker-1", type="localdocker", status="active"
        )
        ElSandboxInstance.objects.create(
            name="sys-1", type="localsystem", status="inactive"
        )
        ElSandboxInstance.objects.create(
            name="docker-2", type="localdocker", status="active"
        )

    def test_filter_by_type(self):
        resp = self.client.get("/api/sandbox/instances/?type=localdocker")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["count"], 2)

    def test_filter_by_status(self):
        resp = self.client.get("/api/sandbox/instances/?status=active")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["count"], 2)

    def test_filter_by_name_icontains(self):
        resp = self.client.get("/api/sandbox/instances/?name=docker")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["content"]["count"], 2)

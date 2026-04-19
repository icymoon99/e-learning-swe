from django.test import TestCase
from django.contrib.auth import get_user_model
from django_q.models import Task, Failure
from rest_framework.test import APIClient

User = get_user_model()


class FailureApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_superuser=False,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_superuser=True,
        )
        # Failure is a proxy model filtering Task(success=False)
        Task.objects.create(
            id="01KPG000000000000000000010",
            name="failed_task",
            func="myapp.tasks.failed",
            args='("arg1",)',
            kwargs="{}",
            started="2026-04-18 12:00:00",
            stopped="2026-04-18 12:00:05",
            success=False,
            result='{"error": "something broke"}',
        )

    def test_list_failures_requires_auth(self):
        resp = self.client.get("/api/q2/failures/")
        self.assertEqual(resp.status_code, 401)

    def test_list_failures(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/failures/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["content"]["count"], 1)

    def test_delete_failure_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        failure = Failure.objects.first()
        resp = self.client.delete(f"/api/q2/failures/{failure.id}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_failure_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        failure = Failure.objects.first()
        failure_id = failure.id
        resp = self.client.delete(f"/api/q2/failures/{failure_id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Failure.objects.filter(id=failure_id).exists())

    def test_retry_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        failure = Failure.objects.first()
        resp = self.client.post(f"/api/q2/failures/{failure.id}/retry/")
        self.assertEqual(resp.status_code, 403)

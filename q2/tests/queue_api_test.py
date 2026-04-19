from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class QueueApiTest(TestCase):
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

    def test_queue_status_requires_auth(self):
        resp = self.client.get("/api/q2/queue/status/")
        self.assertEqual(resp.status_code, 401)

    def test_queue_status(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/queue/status/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("worker_running", data["content"])
        self.assertIn("queue_size", data["content"])

    def test_queue_pause_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/q2/queue/pause/", data={"action": "pause"}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_queue_pause_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/queue/pause/", data={"action": "pause"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_queue_resume_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/queue/pause/", data={"action": "resume"}, format="json")
        self.assertEqual(resp.status_code, 200)

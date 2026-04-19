from django.test import TestCase
from django.contrib.auth import get_user_model
from django_q.models import Task
from rest_framework.test import APIClient

User = get_user_model()


class TaskApiTest(TestCase):
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
        Task.objects.create(
            id="01KPG000000000000000000001",
            name="test_task",
            func="myapp.tasks.test",
            started="2026-04-18 12:00:00",
            stopped="2026-04-18 12:00:05",
            success=True,
            result="ok",
        )

    def test_list_requires_auth(self):
        resp = self.client.get("/api/q2/tasks/")
        self.assertEqual(resp.status_code, 401)

    def test_list_returns_paginated_tasks(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("count", data["content"])
        self.assertIn("results", data["content"])
        self.assertEqual(data["content"]["count"], 1)

    def test_list_filter_by_status_success(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?status=success")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_filter_by_status_failure(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?status=failure")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 0)

    def test_retrieve_task_detail(self):
        self.client.force_authenticate(user=self.user)
        task = Task.objects.first()
        resp = self.client.get(f"/api/q2/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["name"], "test_task")

    def test_list_search_by_name(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?search=test_task")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_search_no_match(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?search=nonexistent")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 0)

    def test_delete_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        task = Task.objects.first()
        resp = self.client.delete(f"/api/q2/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        task = Task.objects.first()
        task_id = task.id
        resp = self.client.delete(f"/api/q2/tasks/{task_id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_delete_nonexistent_task(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.delete("/api/q2/tasks/nonexistent/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 404)

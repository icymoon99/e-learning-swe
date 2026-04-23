"""记忆查询 API 测试。"""

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from agent.models import ElAgent
from task.models import ElTask, ElTaskMemory

User = get_user_model()


class MemoryViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )
        self.client.force_authenticate(user=self.user)

        self.task = ElTask.objects.create(title="测试任务", description="描述")
        self.agent = ElAgent.objects.create(code="test-agent", name="测试Agent")
        self.url = reverse("task-memory-list", kwargs={"task_pk": str(self.task.id)})

    def test_list_memories_success(self):
        """成功获取任务的记忆列表"""
        ElTaskMemory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=1, summary="第一步", status="success",
        )
        ElTaskMemory.objects.create(
            task=self.task, agent=self.agent, thread_id="t2",
            execution_order=2, summary="第二步", status="success",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = response.json()["content"]
        self.assertEqual(content["count"], 2)
        self.assertEqual(content["results"][0]["execution_order"], 1)

    def test_list_memories_empty(self):
        """任务无记忆时返回空列表"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = response.json()["content"]
        self.assertEqual(content["count"], 0)
        self.assertEqual(content["results"], [])

    def test_list_memories_not_found(self):
        """不存在的任务返回 404"""
        url = reverse("task-memory-list", kwargs={"task_pk": "01ARZ3N5K4EN4MSHJWMBFRHYH9"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

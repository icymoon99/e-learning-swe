from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from agent.models import ElAgent
from task.models import ElTask, ElTaskConversation
from sandbox.models import ElSandboxInstance

User = get_user_model()


class ConversationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_superuser=False
        )
        self.task = ElTask.objects.create(
            title="测试任务", description="描述"
        )
        self.sandbox = ElSandboxInstance.objects.create(
            name="test-sandbox", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        self.agent = ElAgent.objects.create(
            code="arch", name="架构师", status="active", sandbox_instance=self.sandbox
        )

    def test_list_requires_auth(self):
        """未认证无法获取对话"""
        resp = self.client.get(
            f"/api/task/tasks/{self.task.id}/conversations/"
        )
        self.assertEqual(resp.status_code, 401)

    def test_list_empty_conversations(self):
        """空对话列表"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(
            f"/api/task/tasks/{self.task.id}/conversations/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 0)

    def test_send_command_requires_auth(self):
        """未认证无法发送指令"""
        resp = self.client.post(
            f"/api/task/tasks/{self.task.id}/conversations/",
            data={"content": "请分析", "agent_code": "arch"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_send_command(self):
        """发送指令创建 user 类型对话"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/task/tasks/{self.task.id}/conversations/",
            data={"content": "请分析架构", "agent_code": "arch"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["comment_type"], "user")
        self.assertEqual(data["content"]["agent_code"], "arch")
        self.assertIn("execution_log_id", data["content"])
        self.assertTrue(
            ElTaskConversation.objects.filter(
                task=self.task,
                comment_type="user",
                content="请分析架构",
            ).exists()
        )

    def test_send_command_invalid_agent(self):
        """Agent 不存在返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/task/tasks/{self.task.id}/conversations/",
            data={"content": "请分析", "agent_code": "nonexistent"},
            format="json",
        )
        self.assertEqual(resp.json()["code"], 1000)  # PARAMETER_ERROR

    def test_send_command_closed_task(self):
        """已关闭任务无法发送指令"""
        self.task.status = "closed"
        self.task.save()
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/task/tasks/{self.task.id}/conversations/",
            data={"content": "请分析", "agent_code": "arch"},
            format="json",
        )
        self.assertEqual(resp.json()["code"], 1)  # ERROR

    def test_list_conversations_with_display_fields(self):
        """对话列表包含显示字段"""
        ElTaskConversation.objects.create(
            task=self.task,
            content="测试内容",
            comment_type="user",
            agent_code="arch",
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(
            f"/api/task/tasks/{self.task.id}/conversations/"
        )
        self.assertEqual(resp.status_code, 200)
        result = resp.json()["content"]["results"][0]
        self.assertIn("comment_type_display", result)
        self.assertIn("agent_name", result)

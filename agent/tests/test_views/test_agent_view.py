from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from agent.models import ElAgent, ElAgentExecutionLog

ElUser = get_user_model()


class TestAgentViewSet(APITestCase):
    """AgentViewSet REST API 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = ElUser.objects.create_user(
            username="testadmin", password="testpass123", is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        ElAgent.objects.create(code="agent_list_a", name="Agent A")
        ElAgent.objects.create(code="agent_list_b", name="Agent B")

    def test_list_agents(self):
        """测试列表接口返回所有 Agent"""
        resp = self.client.get("/api/agent/agents/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["content"]["results"]), 2)

    def test_retrieve_agent(self):
        """测试详情接口返回单个 Agent"""
        agent = ElAgent.objects.get(code="agent_list_a")
        resp = self.client.get(f"/api/agent/agents/{agent.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["code"], "agent_list_a")

    def test_create_agent(self):
        """测试创建 Agent 接口"""
        data = {
            "code": "new_agent",
            "name": "New Agent",
            "description": "A new agent",
            "system_prompt": "You are new",
            "model": "claude-sonnet-4-6",
        }
        resp = self.client.post("/api/agent/agents/", data, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        self.assertEqual(ElAgent.objects.count(), 3)

    def test_update_agent(self):
        """测试更新 Agent 接口"""
        agent = ElAgent.objects.get(code="agent_list_a")
        resp = self.client.patch(
            f"/api/agent/agents/{agent.id}/",
            {"name": "Updated Name"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.json())
        agent.refresh_from_db()
        self.assertEqual(agent.name, "Updated Name")

    def test_delete_agent(self):
        """测试删除 Agent 接口"""
        agent = ElAgent.objects.get(code="agent_list_a")
        count = ElAgent.objects.count()
        resp = self.client.delete(f"/api/agent/agents/{agent.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ElAgent.objects.count(), count - 1)


class TestAgentExecutionLogViewSet(APITestCase):
    """AgentExecutionLogViewSet REST API 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = ElUser.objects.create_user(
            username="testadmin", password="testpass123", is_superuser=True
        )
        self.client.force_authenticate(user=self.user)
        self.agent = ElAgent.objects.create(code="log_api", name="Log API Agent")
        ElAgentExecutionLog.objects.create(
            agent=self.agent, thread_id="thread-1", status="completed"
        )
        ElAgentExecutionLog.objects.create(
            agent=self.agent, thread_id="thread-2", status="running"
        )

    def test_list_logs(self):
        """测试列表接口返回所有执行日志"""
        resp = self.client.get("/api/agent/execution-logs/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["content"]["results"]), 2)

    def test_retrieve_log(self):
        """测试详情接口返回单个日志"""
        log = ElAgentExecutionLog.objects.get(thread_id="thread-1")
        resp = self.client.get(f"/api/agent/execution-logs/{log.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["thread_id"], "thread-1")

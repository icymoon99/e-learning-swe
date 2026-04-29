from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from git_source.models import ElGitSource
from task.models import ElTask, ElTaskConversation
from sandbox.models import ElSandboxInstance

User = get_user_model()


class TaskApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_superuser=False
        )
        self.admin = User.objects.create_user(
            username="admin", password="adminpass123", is_superuser=True
        )
        self.source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
        )
        ElTask.objects.create(
            title="测试任务",
            description="任务描述",
            git_source=self.source,
            source_branch="main",
        )

    def test_list_requires_auth(self):
        """未认证无法列表"""
        resp = self.client.get("/api/task/tasks/")
        self.assertEqual(resp.status_code, 401)

    def test_list_returns_tasks(self):
        """认证用户可获取列表"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/task/tasks/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["content"]["count"], 1)

    def test_list_does_not_expose_token(self):
        """列表不暴露仓库源 token"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/task/tasks/")
        data = resp.json()
        result = data["content"]["results"][0]
        if "git_source" in result and result["git_source"]:
            self.assertNotIn("token", result["git_source"])

    def test_list_filter_by_status(self):
        """按状态过滤"""
        ElTask.objects.create(title="已关闭", description="", status="closed")
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/task/tasks/?status=closed")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_filter_by_git_source(self):
        """按仓库源过滤"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f"/api/task/tasks/?git_source={self.source.id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_search_by_title(self):
        """按标题搜索"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/task/tasks/?search=测试任务")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_create_task(self):
        """创建任务"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/task/tasks/", data={
            "title": "新任务",
            "description": "新任务描述",
            "git_source_id": str(self.source.id),
            "source_branch": "develop",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(ElTask.objects.count(), 2)

    def test_create_task_minimal(self):
        """只传标题即可创建"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/task/tasks/", data={
            "title": "最小任务",
        }, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_retrieve_task(self):
        """获取任务详情"""
        self.client.force_authenticate(user=self.user)
        task = ElTask.objects.first()
        resp = self.client.get(f"/api/task/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("title", data["content"])

    def test_update_task(self):
        """更新任务"""
        self.client.force_authenticate(user=self.user)
        task = ElTask.objects.first()
        resp = self.client.patch(f"/api/task/tasks/{task.id}/", data={
            "title": "修改后的标题",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, "修改后的标题")

    def test_delete_requires_admin(self):
        """非管理员无法删除"""
        self.client.force_authenticate(user=self.user)
        task = ElTask.objects.first()
        resp = self.client.delete(f"/api/task/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_by_admin(self):
        """管理员可删除"""
        self.client.force_authenticate(user=self.admin)
        task = ElTask.objects.first()
        tid = task.id
        resp = self.client.delete(f"/api/task/tasks/{tid}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ElTask.objects.filter(id=tid).exists())

    def test_close_task(self):
        """关闭任务并创建系统对话"""
        self.client.force_authenticate(user=self.user)
        task = ElTask.objects.first()
        resp = self.client.post(f"/api/task/tasks/{task.id}/close/")
        self.assertEqual(resp.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, "closed")
        self.assertTrue(
            task.conversations.filter(comment_type="system").exists()
        )

    def test_close_already_closed_task(self):
        """已关闭的任务再次关闭返回错误"""
        task = ElTask.objects.create(title="关闭任务", description="", status="closed")
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/task/tasks/{task.id}/close/")
        self.assertEqual(resp.json()["code"], 1)

    def test_list_includes_execution_status(self):
        """列表包含最新执行状态"""
        from agent.models import ElAgent, ElAgentExecutionLog
        sandbox = ElSandboxInstance.objects.create(
            name="test-sandbox", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        agent = ElAgent.objects.create(code="arch", name="架构师", sandbox_instance=sandbox)
        task = ElTask.objects.create(title="有执行", description="")
        log = ElAgentExecutionLog.objects.create(
            agent=agent, thread_id="t-1", status="completed"
        )
        ElTaskConversation.objects.create(
            task=task, content="AI", comment_type="ai",
            agent_code="arch", execution_log=log,
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/task/tasks/")
        result = resp.json()["content"]["results"][0]
        self.assertEqual(result.get("latest_execution_status"), "completed")
        self.assertEqual(result.get("latest_execution_agent"), "arch")

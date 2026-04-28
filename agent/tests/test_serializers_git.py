from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog
from agent.serializers import AgentExecutionLogSerializer
from sandbox.models import ElSandboxInstance


class TestAgentExecutionLogSerializerGitFields(TestCase):
    """AgentExecutionLogSerializer Git 字段测试"""

    def setUp(self):
        self.sandbox = ElSandboxInstance.objects.create(name="test-sandbox", type="local")
        self.agent = ElAgent.objects.create(code="ser_git", name="Serializer Git", sandbox_instance=self.sandbox)
        self.log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-ser-git",
            git_pr_url="https://github.com/owner/repo/pull/1",
            git_pr_number=1,
            git_commit_hash="deadbeef",
        )

    def test_git_fields_in_output(self):
        """Git 结果字段应出现在序列化输出中"""
        serializer = AgentExecutionLogSerializer(self.log)
        data = serializer.data
        self.assertIn("git_pr_url", data)
        self.assertIn("git_pr_number", data)
        self.assertIn("git_commit_hash", data)
        self.assertEqual(data["git_pr_url"], "https://github.com/owner/repo/pull/1")
        self.assertEqual(data["git_pr_number"], 1)
        self.assertEqual(data["git_commit_hash"], "deadbeef")

    def test_git_fields_are_read_only(self):
        """Git 字段应为只读，不可通过序列化器写入"""
        serializer = AgentExecutionLogSerializer(
            self.log,
            data={
                "git_pr_url": "https://example.com",
                "git_pr_number": 999,
            },
            partial=True,
        )
        # 只读字段在 valid 数据中会被忽略
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        # 值不应改变
        instance.refresh_from_db()
        self.assertEqual(instance.git_pr_url, "https://github.com/owner/repo/pull/1")

from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog
from sandbox.models import ElSandboxInstance


class TestElAgentExecutionLogGitFields(TestCase):
    """ElAgentExecutionLog Git 结果字段测试"""

    def setUp(self):
        self.sandbox = ElSandboxInstance.objects.create(name="test-sandbox", type="local")
        self.agent = ElAgent.objects.create(code="git_fields", name="Git Fields Agent", sandbox_instance=self.sandbox)

    def test_git_pr_url_default(self):
        """git_pr_url 默认为空字符串"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-git-1",
        )
        self.assertEqual(log.git_pr_url, "")

    def test_git_pr_number_nullable(self):
        """git_pr_number 可以为 None"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-git-2",
        )
        self.assertIsNone(log.git_pr_number)

    def test_git_commit_hash_default(self):
        """git_commit_hash 默认为空字符串"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-git-3",
        )
        self.assertEqual(log.git_commit_hash, "")

    def test_can_store_git_results(self):
        """可以存储 Git 工作流结果"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-git-4",
            git_pr_url="https://github.com/owner/repo/pull/42",
            git_pr_number=42,
            git_commit_hash="abc123def456",
        )
        self.assertEqual(log.git_pr_url, "https://github.com/owner/repo/pull/42")
        self.assertEqual(log.git_pr_number, 42)
        self.assertEqual(log.git_commit_hash, "abc123def456")

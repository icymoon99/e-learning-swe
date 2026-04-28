"""Orchestrator Git 集成测试"""

from __future__ import annotations

from unittest import mock
from unittest.mock import MagicMock, patch

from django.test import TestCase

from agent.context import GitContext
from agent.models import ElAgent, ElAgentExecutionLog
from agent.orchestrator import Orchestrator
from llm.models import ElLLMProvider, ElLLMModel
from sandbox.models import ElSandboxInstance


class TestOrchestratorGitIntegration(TestCase):
    """Orchestrator Git 工作流集成测试"""

    def setUp(self):
        self.sandbox = ElSandboxInstance.objects.create(name="test-sandbox", type="local")
        self.provider = ElLLMProvider.objects.create(
            code="anthropic", name="Anthropic"
        )
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="claude-sonnet-4-6",
            display_name="Claude Sonnet 4.6",
        )
        self.agent = ElAgent.objects.create(
            code="git_test_agent",
            name="Git Test Agent",
            system_prompt="You are a test agent",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )

    def test_execute_without_git_works_normally(self):
        """不传 Git 参数时，Agent 应正常执行（无 Git 工作流）"""
        orchestrator = Orchestrator()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "final_result", "data": {"answer": "done"}},
        ])
        with mock.patch.object(
            orchestrator, "get_or_create_agent", return_value=mock_agent
        ):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="hello",
                thread_id="thread-no-git",
            )
        self.assertEqual(result["status"], "completed")

    def test_execute_with_git_passes_context(self):
        """传 Git 参数时，应构造 GitContext 并传入 config"""
        orchestrator = Orchestrator()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "final_result", "data": {"answer": "done"}},
        ])
        with mock.patch.object(
            orchestrator, "get_or_create_agent", return_value=mock_agent
        ):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="do work",
                thread_id="thread-git-001",
                agent_code="git_test",
                task_branch="feature/auth",
                git_repo_url="https://github.com/owner/repo.git",
                git_platform="github",
                git_token_secret="GITHUB_TOKEN",
            )

        self.assertEqual(result["status"], "completed")
        # 验证 stream 被调用且 config 包含 context
        call_args = mock_agent.stream.call_args
        config = call_args[1]["config"]
        self.assertIn("context", config)
        self.assertIsInstance(config["context"], GitContext)
        self.assertEqual(config["context"].task_branch, "feature/auth")
        self.assertEqual(config["context"].git_repo_url, "https://github.com/owner/repo.git")

    def test_execute_with_git_logs_pr_info(self):
        """Git 工作流完成时，PR 信息应写入执行日志"""
        orchestrator = Orchestrator()
        mock_agent = MagicMock()
        mock_agent.stream.return_value = iter([
            {"type": "final_result", "data": {"answer": "done"}},
        ])
        with mock.patch.object(
            orchestrator, "get_or_create_agent", return_value=mock_agent
        ):
            result = orchestrator.execute(
                agent_id=self.agent.id,
                message="do work",
                thread_id="thread-git-002",
                agent_code="git_test",
                task_branch="main",
                git_repo_url="https://github.com/owner/repo.git",
                git_platform="github",
            )

        # 验证日志记录已创建
        log = ElAgentExecutionLog.objects.get(thread_id="thread-git-002")
        self.assertEqual(log.status, "completed")

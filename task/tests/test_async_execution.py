from unittest.mock import patch
from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog
from task.models import ElTask, ElTaskConversation


class AsyncExecutionTest(TestCase):
    def setUp(self):
        self.agent = ElAgent.objects.create(
            code="coder", name="编码师",
            system_prompt="你是一个编码助手",
            status="active",
        )
        self.task = ElTask.objects.create(
            title="异步任务", description="描述"
        )
        self.conv = ElTaskConversation.objects.create(
            task=self.task,
            content="帮我写代码",
            comment_type="user",
            agent_code="coder",
        )
        self.log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id=f"task-{self.task.id}-{self.conv.id}",
            status="running",
        )

    @patch("agent.orchestrator.orchestrator.execute")
    def test_execute_conversation_success(self, mock_execute):
        """正常执行完成"""
        mock_execute.return_value = {
            "status": "completed",
            "result": "代码编写完成",
            "error_message": None,
            "execution_log_id": str(self.log.id),
        }

        from task.tasks import execute_task_conversation
        execute_task_conversation(
            str(self.conv.id),
            "coder",
            str(self.task.id),
            str(self.log.id),
        )

        # 执行日志更新为 completed
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, "completed")

        # 创建 AI 类型对话
        ai_conv = ElTaskConversation.objects.filter(
            task=self.task,
            comment_type="ai",
        ).first()
        self.assertIsNotNone(ai_conv)
        self.assertEqual(ai_conv.agent_code, "coder")

    @patch("agent.orchestrator.orchestrator.execute")
    def test_execute_conversation_failure(self, mock_execute):
        """执行失败"""
        mock_execute.side_effect = Exception("LLM API 超时")

        from task.tasks import execute_task_conversation
        execute_task_conversation(
            str(self.conv.id),
            "coder",
            str(self.task.id),
            str(self.log.id),
        )

        # 执行日志更新为 failed
        self.log.refresh_from_db()
        self.assertEqual(self.log.status, "failed")
        self.assertIn("LLM API 超时", self.log.error_message)

    def test_execute_with_nonexistent_conversation(self):
        """不存在的对话 ID 不做处理"""
        from task.tasks import execute_task_conversation
        # 不应抛异常，而是记录日志后返回
        execute_task_conversation(
            "01KPG000000000000000000099",
            "coder",
            str(self.task.id),
            str(self.log.id),
        )
        # 验证无新对话创建
        self.assertEqual(
            ElTaskConversation.objects.filter(
                comment_type="ai"
            ).count(),
            0,
        )

    @patch("agent.orchestrator.orchestrator.execute")
    def test_execute_with_git_source(self, mock_execute):
        """带仓库源的任务执行"""
        mock_execute.return_value = {
            "status": "completed",
            "result": "分析完成",
            "error_message": None,
            "execution_log_id": "01KPG000000000000000000001",
        }
        from git_source.models import ElGitSource
        source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
        )
        task_with_source = ElTask.objects.create(
            title="有仓库任务",
            description="描述",
            git_source=source,
            source_branch="develop",
        )
        conv = ElTaskConversation.objects.create(
            task=task_with_source,
            content="分析代码",
            comment_type="user",
            agent_code="coder",
        )
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id=f"task-{task_with_source.id}-{conv.id}",
            status="running",
        )

        from task.tasks import execute_task_conversation
        execute_task_conversation(
            str(conv.id), "coder", str(task_with_source.id), str(log.id)
        )

        # 验证 orchestrator.execute 传入了 git 配置
        mock_execute.assert_called_once()
        call_kwargs = mock_execute.call_args[1]
        self.assertEqual(
            call_kwargs["git_repo_url"],
            "https://github.com/owner/repo.git",
        )
        self.assertEqual(call_kwargs["task_branch"], "develop")

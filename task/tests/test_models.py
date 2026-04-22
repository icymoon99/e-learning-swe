from django.test import TestCase
from git_source.models import ElGitSource
from agent.models import ElAgent, ElAgentExecutionLog
from task.models import ElTask, ElTaskConversation


class ElTaskModelTest(TestCase):
    def setUp(self):
        self.source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
        )

    def test_create_task(self):
        """创建任务"""
        task = ElTask.objects.create(
            title="测试任务",
            description="任务描述",
            git_source=self.source,
            source_branch="main",
        )
        self.assertEqual(task.title, "测试任务")
        self.assertEqual(task.status, "open")
        self.assertIsNotNone(task.id)

    def test_create_task_without_git_source(self):
        """任务可以不关联仓库源"""
        task = ElTask.objects.create(
            title="无仓库任务",
            description="纯咨询",
        )
        self.assertIsNone(task.git_source)

    def test_default_status_is_open(self):
        """默认状态为 open"""
        task = ElTask.objects.create(title="默认状态", description="")
        self.assertEqual(task.status, "open")

    def test_str_representation(self):
        """字符串表示"""
        task = ElTask.objects.create(title="标题测试", description="")
        self.assertEqual(str(task), "标题测试")


class ElTaskConversationModelTest(TestCase):
    def setUp(self):
        self.task = ElTask.objects.create(title="任务", description="描述")
        self.agent = ElAgent.objects.create(code="arch", name="架构师")

    def test_create_user_conversation(self):
        """创建用户指令对话"""
        conv = ElTaskConversation.objects.create(
            task=self.task,
            content="用户指令",
            comment_type="user",
        )
        self.assertEqual(conv.content, "用户指令")
        self.assertEqual(conv.comment_type, "user")
        self.assertIsNone(conv.agent_code)

    def test_create_ai_conversation_with_agent(self):
        """创建 AI 回复对话（关联 Agent 和执行日志）"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-1",
            status="completed",
        )
        conv = ElTaskConversation.objects.create(
            task=self.task,
            content="AI 回复",
            comment_type="ai",
            agent_code="arch",
            execution_log=log,
        )
        self.assertEqual(conv.execution_log.id, log.id)
        self.assertEqual(conv.agent_code, "arch")

    def test_conversation_ordering(self):
        """对话按创建时间排序"""
        c1 = ElTaskConversation.objects.create(
            task=self.task, content="第一条", comment_type="user"
        )
        c2 = ElTaskConversation.objects.create(
            task=self.task, content="第二条", comment_type="ai"
        )
        conversations = list(self.task.conversations.all())
        self.assertEqual(conversations[0].content, "第一条")
        self.assertEqual(conversations[1].content, "第二条")

    def test_related_name_conversations(self):
        """通过 related_name 获取对话列表"""
        ElTaskConversation.objects.create(
            task=self.task, content="对话1", comment_type="user"
        )
        ElTaskConversation.objects.create(
            task=self.task, content="对话2", comment_type="ai"
        )
        self.assertEqual(self.task.conversations.count(), 2)

    def test_comment_type_display(self):
        """对话类型显示文本"""
        conv = ElTaskConversation.objects.create(
            task=self.task, content="测试", comment_type="system"
        )
        self.assertEqual(conv.get_comment_type_display(), "系统通知")

    def test_str_representation(self):
        """字符串表示"""
        conv = ElTaskConversation.objects.create(
            task=self.task, content="这是一条测试内容", comment_type="user"
        )
        self.assertIn("用户指令", str(conv))

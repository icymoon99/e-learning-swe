from django.test import TestCase
from git_source.models import ElGitSource
from agent.models import ElAgent, ElAgentExecutionLog
from task.models import ElTask, ElTaskConversation
from sandbox.models import ElSandboxInstance


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
        self.sandbox = ElSandboxInstance.objects.create(
            name="test-sandbox", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        self.agent = ElAgent.objects.create(code="arch", name="架构师", sandbox_instance=self.sandbox)

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


class ElTaskMemoryModelTest(TestCase):
    def setUp(self):
        from task.models import ElTaskMemory
        self.Memory = ElTaskMemory
        self.source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
        )
        self.task = ElTask.objects.create(
            title="测试任务",
            description="任务描述",
            git_source=self.source,
            source_branch="main",
        )
        self.sandbox = ElSandboxInstance.objects.create(
            name="test-sandbox", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        self.agent = ElAgent.objects.create(code="analyzer", name="代码分析器", sandbox_instance=self.sandbox)

    def test_create_task_memory_success(self):
        """成功创建任务记忆"""
        memory = self.Memory.objects.create(
            task=self.task,
            agent=self.agent,
            thread_id="thread-001",
            execution_order=1,
            summary="分析项目结构，识别3个需重构模块",
            status="success",
        )
        self.assertIsNotNone(memory.id)
        self.assertEqual(memory.execution_order, 1)
        self.assertEqual(memory.status, "success")
        self.assertEqual(memory.summary, "分析项目结构，识别3个需重构模块")

    def test_create_memory_with_pr_info(self):
        """创建包含 PR 信息的记忆"""
        memory = self.Memory.objects.create(
            task=self.task,
            agent=self.agent,
            thread_id="thread-001",
            execution_order=1,
            summary="完成用户认证模块",
            commit_message="feat: add user auth module",
            pr_url="https://github.com/owner/repo/pull/1",
            commit_hash="abc123def456",
            status="success",
        )
        self.assertEqual(memory.pr_url, "https://github.com/owner/repo/pull/1")
        self.assertEqual(memory.commit_hash, "abc123def456")
        self.assertEqual(memory.commit_message, "feat: add user auth module")

    def test_create_failed_memory(self):
        """记录失败的 Agent 执行"""
        memory = self.Memory.objects.create(
            task=self.task,
            agent=self.agent,
            thread_id="thread-001",
            execution_order=1,
            summary="尝试重构但失败",
            status="failed",
            error_message="数据库连接超时",
        )
        self.assertEqual(memory.status, "failed")
        self.assertIn("超时", memory.error_message)

    def test_memory_ordering(self):
        """记忆按 execution_order 排序"""
        self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t2",
            execution_order=2, summary="第二步", status="success",
        )
        self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=1, summary="第一步", status="success",
        )
        memories = list(self.Memory.objects.filter(task=self.task).order_by("execution_order"))
        self.assertEqual(memories[0].execution_order, 1)
        self.assertEqual(memories[1].execution_order, 2)

    def test_task_delete_cascades_to_memories(self):
        """任务删除时，记忆级联删除"""
        self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=1, summary="测试", status="success",
        )
        task_id = self.task.id
        self.task.delete()
        self.assertEqual(self.Memory.objects.filter(task_id=task_id).count(), 0)

    def test_agent_delete_sets_memory_agent_null(self):
        """Agent 删除时，记忆中 agent 字段置空"""
        memory = self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=1, summary="测试", status="success",
        )
        self.agent.delete()
        memory.refresh_from_db()
        self.assertIsNone(memory.agent)

    def test_task_related_name_memories(self):
        """通过 related_name 获取记忆列表"""
        self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=1, summary="记忆1", status="success",
        )
        self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t2",
            execution_order=2, summary="记忆2", status="success",
        )
        self.assertEqual(self.task.memories.count(), 2)

    def test_str_representation(self):
        """字符串表示"""
        memory = self.Memory.objects.create(
            task=self.task, agent=self.agent, thread_id="t1",
            execution_order=3, summary="测试", status="success",
        )
        self.assertIn("TaskMemory", str(memory))
        self.assertIn("3", str(memory))

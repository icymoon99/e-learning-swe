"""TaskMemoryMiddleware 单元测试。"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from agent.models import ElAgent
from task.models import ElTask, ElTaskMemory


class TaskMemoryMiddlewareBeforeAgentTest(TestCase):
    """before_agent 钩子测试"""

    def setUp(self):
        from task.middleware.task_memory import TaskMemoryMiddleware

        self.task = ElTask.objects.create(title="测试任务", description="描述")
        self.mw = TaskMemoryMiddleware(task_id=str(self.task.id))
        self.agent = ElAgent.objects.create(code="analyzer", name="分析器")

    def test_no_memories_returns_early(self):
        """无历史记忆时直接返回"""
        with patch.object(self.mw, "_get_memories", return_value=[]):
            state = {"system_prompt": "你是一个AI助手"}
            runtime = MagicMock()
            result = self.mw.before_agent(state, runtime)
            self.assertIsNone(result)
            self.assertEqual(state["system_prompt"], "你是一个AI助手")

    def test_injects_full_memory_when_under_limit(self):
        """记忆未超过 token 阈值时，完整注入"""
        memory = ElTaskMemory(
            task=self.task,
            agent=self.agent,
            thread_id="t1",
            execution_order=1,
            summary="分析完成",
            status="success",
        )

        with patch.object(self.mw, "_get_memories", return_value=[memory]):
            with patch.object(self.mw, "_estimate_tokens", return_value=100):
                state = {"system_prompt": "你是一个AI助手"}
                runtime = MagicMock()
                self.mw.before_agent(state, runtime)
                self.assertIn("## 任务历史记忆", state["system_prompt"])
                self.assertIn("分析完成", state["system_prompt"])

    def test_summarizes_when_over_limit(self):
        """记忆超过 token 阈值时，调用摘要"""
        memory = ElTaskMemory(
            task=self.task,
            agent=self.agent,
            thread_id="t1",
            execution_order=1,
            summary="分析完成",
            status="success",
        )

        with patch.object(self.mw, "_get_memories", return_value=[memory]):
            with patch.object(self.mw, "_estimate_tokens", return_value=10000):
                with patch.object(
                    self.mw, "_summarize_memories", return_value="任务进度摘要"
                ) as mock_sum:
                    state = {"system_prompt": "你是一个AI助手"}
                    runtime = MagicMock()
                    self.mw.before_agent(state, runtime)
                    mock_sum.assert_called_once()
                    self.assertIn("任务进度摘要", state["system_prompt"])


class TaskMemoryMiddlewareAfterAgentTest(TestCase):
    """after_agent 钩子测试"""

    def setUp(self):
        from task.middleware.task_memory import TaskMemoryMiddleware

        self.task = ElTask.objects.create(title="测试任务", description="描述")
        self.mw = TaskMemoryMiddleware(task_id=str(self.task.id))

    def test_saves_memory_on_success(self):
        """Agent 成功执行后，保存记忆"""
        agent = ElAgent.objects.create(code="test-agent", name="测试Agent")

        state = {
            "agent_output": {
                "summary": "完成工作",
                "commit_message": "feat: add feature",
            },
            "git_pr_url": "https://github.com/owner/repo/pull/1",
            "git_commit_hash": "abc123",
        }
        runtime = MagicMock()
        runtime.config.configurable = {"agent_code": "test-agent"}

        with patch(
            "task.middleware.task_memory.ElAgent.objects.get", return_value=agent
        ):
            with patch("task.middleware.task_memory.ElTaskMemory") as MockMemory:
                MockMemory.objects.filter.return_value.count.return_value = 0

                self.mw.after_agent(state, runtime, success=True)

                MockMemory.objects.create.assert_called_once()
                call_kwargs = MockMemory.objects.create.call_args[1]
                self.assertEqual(call_kwargs["summary"], "完成工作")
                self.assertEqual(
                    call_kwargs["pr_url"], "https://github.com/owner/repo/pull/1"
                )
                self.assertEqual(call_kwargs["status"], "success")

    def test_saves_memory_on_failure(self):
        """Agent 执行失败时，保存错误信息"""
        agent = ElAgent.objects.create(code="test-agent", name="测试Agent")

        with patch("task.middleware.task_memory.ElAgent.objects.get", return_value=agent):
            with patch("task.middleware.task_memory.ElTaskMemory") as MockMemory:
                MockMemory.objects.filter.return_value.count.return_value = 0
                MockMemory.objects.create.return_value = MagicMock()

                state = {"error_message": "数据库连接超时"}
                runtime = MagicMock()
                runtime.config.configurable = {"agent_code": "test-agent"}

                self.mw.after_agent(state, runtime, success=False)

                call_kwargs = MockMemory.objects.create.call_args[1]
                self.assertEqual(call_kwargs["status"], "failed")
                self.assertIn("数据库连接超时", call_kwargs["error_message"])

    def test_agent_not_found_logs_warning(self):
        """Agent 不存在时，agent 字段为 None"""
        with patch("task.middleware.task_memory.ElAgent.objects.get", side_effect=ElAgent.DoesNotExist):
            with patch("task.middleware.task_memory.ElTaskMemory") as MockMemory:
                MockMemory.objects.filter.return_value.count.return_value = 0
                MockMemory.objects.create.return_value = MagicMock()

                state = {"agent_output": {"summary": "完成工作"}}
                runtime = MagicMock()
                runtime.config.configurable = {"agent_code": "nonexistent"}

                self.mw.after_agent(state, runtime, success=True)

                call_kwargs = MockMemory.objects.create.call_args[1]
                self.assertIsNone(call_kwargs["agent"])


class TaskMemoryMiddlewareInternalTest(TestCase):
    """内部方法测试"""

    def setUp(self):
        from task.middleware.task_memory import TaskMemoryMiddleware

        self.task = ElTask.objects.create(title="内部测试任务", description="描述")
        self.mw = TaskMemoryMiddleware(task_id=str(self.task.id))
        self.agent = ElAgent.objects.create(code="int-test", name="内部测试")

    def test_format_memories(self):
        """格式化记忆为结构化文本"""
        m1 = ElTaskMemory(
            task=self.task,
            agent=self.agent,
            thread_id="t1",
            execution_order=1,
            summary="分析项目结构",
            status="success",
        )
        m2 = ElTaskMemory(
            task=self.task,
            agent=self.agent,
            thread_id="t2",
            execution_order=2,
            summary="重构认证模块",
            commit_message="feat: refactor auth",
            pr_url="https://github.com/owner/repo/pull/1",
            status="success",
        )
        result = self.mw._format_memories([m1, m2])
        self.assertIn("[第1步 - 内部测试]", result)
        self.assertIn("分析项目结构", result)
        self.assertIn("[第2步 - 内部测试]", result)
        self.assertIn("重构认证模块", result)
        self.assertIn("feat: refactor auth", result)
        self.assertIn("https://github.com/owner/repo/pull/1", result)

    def test_parse_agent_output_from_dict(self):
        """从 agent_output dict 中解析"""
        state = {
            "agent_output": {
                "summary": "自定义摘要",
                "commit_message": "feat: custom",
            }
        }
        summary, commit = self.mw._parse_agent_output(state)
        self.assertEqual(summary, "自定义摘要")
        self.assertEqual(commit, "feat: custom")

    def test_parse_agent_output_fallback(self):
        """无法解析时使用默认值"""
        state = {"messages": []}
        summary, commit = self.mw._parse_agent_output(state)
        self.assertEqual(summary, "Agent 完成工作")
        self.assertEqual(commit, "feat: agent 完成工作")

    def test_estimate_tokens(self):
        """token 估算委托给 summarizer"""
        result = self.mw._estimate_tokens("测试文本")
        self.assertIsInstance(result, int)

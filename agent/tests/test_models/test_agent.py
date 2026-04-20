from django.test import TestCase
from django.db import IntegrityError
from agent.models import ElAgent, ElAgentExecutionLog, AGENT_STATUS_CHOICES, EXECUTION_STATUS_CHOICES


class TestElAgent(TestCase):
    """ElAgent 模型测试"""

    def test_create_agent_with_defaults(self):
        """测试创建 Agent 并使用默认值"""
        agent = ElAgent.objects.create(
            code="code_review",
            name="代码审查 Agent",
            description="自动审查代码质量",
            system_prompt="你是一个代码审查助手",
            model="claude-sonnet-4-6",
        )
        self.assertEqual(agent.code, "code_review")
        self.assertEqual(agent.status, "active")
        self.assertEqual(agent.metadata, {})
        self.assertIsNotNone(agent.id)
        self.assertIsNotNone(agent.created_at)
        self.assertIsNotNone(agent.updated_at)

    def test_agent_status_choices(self):
        """测试状态选项包含 active/inactive/deleted"""
        choices = [c[0] for c in AGENT_STATUS_CHOICES]
        self.assertIn("active", choices)
        self.assertIn("inactive", choices)
        self.assertIn("deleted", choices)

    def test_agent_code_must_be_unique(self):
        """测试 code 字段唯一性约束"""
        ElAgent.objects.create(code="test", name="Test Agent")
        with self.assertRaises(IntegrityError):
            ElAgent.objects.create(code="test", name="Duplicate Agent")

    def test_agent_str_representation(self):
        """测试 __str__ 返回名称和编码"""
        agent = ElAgent.objects.create(code="reviewer", name="Reviewer")
        self.assertIn("Reviewer", str(agent))
        self.assertIn("reviewer", str(agent))

    def test_agent_metadata_can_store_complex_data(self):
        """测试 metadata 可以存储复杂嵌套数据"""
        agent = ElAgent.objects.create(
            code="complex",
            name="Complex Agent",
            metadata={
                "sub_agents": [{"name": "sub1", "tools": ["search"]}],
                "hitl_tools": ["interrupt_request"],
            },
        )
        self.assertEqual(agent.metadata["sub_agents"][0]["name"], "sub1")


class TestElAgentExecutionLog(TestCase):
    """ElAgentExecutionLog 模型测试"""

    def setUp(self):
        self.agent = ElAgent.objects.create(code="test", name="Test Agent")

    def test_create_execution_log_with_defaults(self):
        """测试创建执行日志并使用默认值"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-001",
        )
        self.assertEqual(log.agent.id, self.agent.id)
        self.assertEqual(log.thread_id, "thread-001")
        self.assertEqual(log.status, "running")
        self.assertEqual(log.events, [])
        self.assertIsNone(log.result)
        self.assertEqual(log.error_message, "")

    def test_execution_status_choices(self):
        """测试执行状态选项"""
        choices = [c[0] for c in EXECUTION_STATUS_CHOICES]
        self.assertIn("running", choices)
        self.assertIn("completed", choices)
        self.assertIn("failed", choices)

    def test_multiple_threads_same_agent(self):
        """测试同一 Agent 可有多 thread 并行记录"""
        ElAgentExecutionLog.objects.create(agent=self.agent, thread_id="t1", status="completed")
        ElAgentExecutionLog.objects.create(agent=self.agent, thread_id="t2", status="running")
        self.assertEqual(ElAgentExecutionLog.objects.filter(agent=self.agent).count(), 2)

    def test_events_store_raw_data(self):
        """测试 events 字段存储原始事件数据"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-raw",
            events=[
                {"type": "tool_call", "data": {"name": "search"}},
                {"type": "final_result", "data": {"answer": "done"}},
            ],
        )
        self.assertEqual(len(log.events), 2)
        self.assertEqual(log.events[1]["data"]["answer"], "done")

    def test_result_stores_final_output(self):
        """测试 result 字段存储最终执行结果"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-result",
            status="completed",
            result={"final_answer": "The answer is 42"},
        )
        self.assertEqual(log.result["final_answer"], "The answer is 42")

    def test_error_message_stored_on_failure(self):
        """测试失败时记录错误信息"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-error",
            status="failed",
            error_message="LLM connection timeout",
        )
        self.assertEqual(log.status, "failed")
        self.assertIn("timeout", log.error_message)

    def test_execution_str_representation(self):
        """测试 __str__ 返回可读信息"""
        log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-str",
            status="completed",
        )
        self.assertIn("Test Agent", str(log))
        self.assertIn("completed", str(log))

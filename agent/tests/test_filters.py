from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog
from agent.filters import ElAgentFilter, ElAgentExecutionLogFilter


class TestElAgentFilter(TestCase):
    """ElAgentFilter 测试"""

    def setUp(self):
        ElAgent.objects.create(code="agent_a", name="Agent Alpha", status="active")
        ElAgent.objects.create(code="agent_b", name="Agent Beta", status="inactive")
        ElAgent.objects.create(code="agent_c", name="Searchable Agent", status="active")

    def test_filter_by_status(self):
        """测试按状态过滤"""
        f = ElAgentFilter({"status": "active"}, queryset=ElAgent.objects.all())
        self.assertEqual(f.qs.count(), 2)

    def test_filter_by_code_exact(self):
        """测试按编码精确匹配"""
        f = ElAgentFilter({"code": "agent_a"}, queryset=ElAgent.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first().code, "agent_a")

    def test_filter_by_name_icontains(self):
        """测试按名称模糊搜索"""
        f = ElAgentFilter({"name": "search"}, queryset=ElAgent.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_no_params(self):
        """测试无参数时返回全部"""
        f = ElAgentFilter({}, queryset=ElAgent.objects.all())
        self.assertEqual(f.qs.count(), 3)


class TestElAgentExecutionLogFilter(TestCase):
    """ElAgentExecutionLogFilter 测试"""

    def setUp(self):
        self.agent = ElAgent.objects.create(code="log_filter", name="Log Filter Agent")
        ElAgentExecutionLog.objects.create(agent=self.agent, thread_id="thread-a", status="completed")
        ElAgentExecutionLog.objects.create(agent=self.agent, thread_id="thread-b", status="running")
        ElAgentExecutionLog.objects.create(agent=self.agent, thread_id="unique-thread", status="failed")

    def test_filter_by_status(self):
        """测试按执行状态过滤"""
        f = ElAgentExecutionLogFilter({"status": "completed"}, queryset=ElAgentExecutionLog.objects.all())
        self.assertEqual(f.qs.count(), 1)

    def test_filter_by_agent(self):
        """测试按 Agent ID 过滤"""
        f = ElAgentExecutionLogFilter(
            {"agent": str(self.agent.id)}, queryset=ElAgentExecutionLog.objects.all()
        )
        self.assertEqual(f.qs.count(), 3)

    def test_filter_by_thread_id_icontains(self):
        """测试按 thread_id 模糊搜索"""
        f = ElAgentExecutionLogFilter({"thread_id": "unique"}, queryset=ElAgentExecutionLog.objects.all())
        self.assertEqual(f.qs.count(), 1)

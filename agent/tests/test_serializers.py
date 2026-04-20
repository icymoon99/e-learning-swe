from django.test import TestCase
from agent.models import ElAgent, ElAgentExecutionLog
from agent.serializers import AgentSerializer, AgentExecutionLogSerializer


class TestAgentSerializer(TestCase):
    """AgentSerializer 测试"""

    def setUp(self):
        self.agent = ElAgent.objects.create(
            code="serializer_test",
            name="Serializer Test Agent",
            description="Testing serializer",
            system_prompt="You are a test agent",
            model="claude-sonnet-4-6",
        )

    def test_valid_serialization(self):
        """测试有效数据序列化"""
        data = {
            "code": "data_analysis",
            "name": "数据分析 Agent",
            "description": "分析数据并生成报告",
            "system_prompt": "你是一个数据分析助手",
            "model": "claude-sonnet-4-6",
        }
        serializer = AgentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_code_is_required(self):
        """测试 code 字段必填"""
        serializer = AgentSerializer(data={"name": "Test"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_name_has_default(self):
        """测试 name 字段有默认值，不传也可以"""
        serializer = AgentSerializer(data={"code": "test"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.name, "")

    def test_read_only_fields_in_output(self):
        """测试只读字段出现在序列化输出中"""
        serializer = AgentSerializer(self.agent)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("status_display", data)
        self.assertEqual(data["code"], "serializer_test")

    def test_status_display_field(self):
        """测试 status_display 返回中文标签"""
        serializer = AgentSerializer(self.agent)
        self.assertEqual(serializer.data["status_display"], "启用")

    def test_update_via_serializer(self):
        """测试通过序列化器更新数据"""
        serializer = AgentSerializer(self.agent, data={"code": "updated", "name": "Updated"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.name, "Updated")


class TestAgentExecutionLogSerializer(TestCase):
    """AgentExecutionLogSerializer 测试"""

    def setUp(self):
        self.agent = ElAgent.objects.create(code="exec_test", name="Exec Test")
        self.log = ElAgentExecutionLog.objects.create(
            agent=self.agent,
            thread_id="thread-serial",
            status="completed",
            result={"answer": "done"},
        )

    def test_read_only_fields(self):
        """测试只读字段和关联字段"""
        serializer = AgentExecutionLogSerializer(self.log)
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("agent_code", data)
        self.assertIn("agent_name", data)
        self.assertIn("status_display", data)
        self.assertEqual(data["agent_code"], "exec_test")
        self.assertEqual(data["agent_name"], "Exec Test")

    def test_events_field_serialized(self):
        """测试 events 字段序列化"""
        self.log.events = [{"type": "tool_call"}]
        self.log.save()
        serializer = AgentExecutionLogSerializer(self.log)
        self.assertEqual(len(serializer.data["events"]), 1)

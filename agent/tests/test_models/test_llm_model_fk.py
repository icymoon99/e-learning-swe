from django.test import TestCase
from django.db import IntegrityError

from agent.models import ElAgent, ElAgentExecutionLog
from llm.models import ElLLMProvider, ElLLMModel
from sandbox.models import ElSandboxInstance


class ElAgentLLMModelFKTest(TestCase):
    """ElAgent llm_model 外键关联测试"""

    def setUp(self):
        self.sandbox = ElSandboxInstance.objects.create(name="test-sandbox", type="local")
        self.provider = ElLLMProvider.objects.create(
            code="openai", name="OpenAI"
        )
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="gpt-4o",
            display_name="GPT-4o",
        )

    def test_llm_model_foreign_key(self):
        """Agent 可通过 llm_model FK 关联 LLM 模型"""
        agent = ElAgent.objects.create(
            code="test_agent",
            name="Test Agent",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )
        self.assertEqual(agent.llm_model.id, self.llm_model.id)
        self.assertEqual(agent.llm_model.model_code, "gpt-4o")

    def test_llm_model_can_be_null(self):
        """llm_model 允许为空（兼容历史数据或尚未配置模型的 Agent）"""
        agent = ElAgent.objects.create(
            code="no_model_agent",
            name="No Model Agent",
            sandbox_instance=self.sandbox,
        )
        self.assertIsNone(agent.llm_model)

    def test_protect_on_delete_llm_model(self):
        """删除被 Agent 引用的 LLM 模型时触发 ProtectedError"""
        agent = ElAgent.objects.create(
            code="protected_agent",
            name="Protected Agent",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )
        with self.assertRaises(IntegrityError):
            self.llm_model.delete()

    def test_reverse_lookup_from_llm_model(self):
        """可通过 related_name agents 从 LLM 模型反向查询 Agent"""
        ElAgent.objects.create(
            code="agent1", name="Agent 1", llm_model=self.llm_model, sandbox_instance=self.sandbox
        )
        ElAgent.objects.create(
            code="agent2", name="Agent 2", llm_model=self.llm_model, sandbox_instance=self.sandbox
        )
        self.assertEqual(self.llm_model.agents.count(), 2)

    def test_str_representation_with_model(self):
        """__str__ 包含关联模型信息"""
        agent = ElAgent.objects.create(
            code="str_agent",
            name="String Agent",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )
        agent.refresh_from_db()
        self.assertIn("String Agent", str(agent))

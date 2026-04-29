"""测试 sandbox_resolver 的 thread_id 传递"""

from unittest import mock
from django.test import TestCase
from agent.models import ElAgent
from agent.services.sandbox_resolver import resolve_backend
from llm.models import ElLLMProvider, ElLLMModel
from sandbox.models import ElSandboxInstance


class TestResolveBackendThreadId(TestCase):
    """测试 resolve_backend 传递 thread_id 到 get_backend"""

    def setUp(self):
        self.sandbox = ElSandboxInstance.objects.create(
            name="test-sandbox", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )
        self.provider = ElLLMProvider.objects.create(
            code="anthropic", name="Anthropic"
        )
        self.llm_model = ElLLMModel.objects.create(
            provider=self.provider,
            model_code="claude-sonnet-4-6",
            display_name="Claude Sonnet 4.6",
        )
        self.agent = ElAgent.objects.create(
            code="test_agent",
            name="Test Agent",
            system_prompt="You are a test agent",
            llm_model=self.llm_model,
            sandbox_instance=self.sandbox,
        )

    def test_resolve_backend_passes_thread_id(self):
        """resolve_backend 应将 thread_id 传递给 get_backend"""
        with mock.patch("sandbox.backends.get_backend") as mock_get:
            mock_backend = mock.MagicMock()
            mock_get.return_value = mock_backend
            resolve_backend(self.agent, thread_id="abc123")
            mock_get.assert_called_once_with(self.agent.sandbox_instance, thread_id="abc123")

    def test_resolve_backend_default_empty_thread_id(self):
        """不传 thread_id 时应使用空字符串"""
        with mock.patch("sandbox.backends.get_backend") as mock_get:
            mock_backend = mock.MagicMock()
            mock_get.return_value = mock_backend
            resolve_backend(self.agent)
            mock_get.assert_called_once_with(self.agent.sandbox_instance, thread_id="")

    def test_resolve_backend_raises_on_inactive_sandbox(self):
        """沙箱未启动时应抛出 ApiException"""
        self.sandbox.status = "inactive"
        self.sandbox.save()
        from core.common.exception.api_exception import ApiException
        with self.assertRaises(ApiException) as ctx:
            resolve_backend(self.agent, thread_id="xyz")
        self.assertIn("未启动", str(ctx.exception))

    def test_resolve_backend_raises_on_error_sandbox(self):
        """沙箱状态异常时应抛出 ApiException"""
        self.sandbox.status = "error"
        self.sandbox.save()
        from core.common.exception.api_exception import ApiException
        with self.assertRaises(ApiException) as ctx:
            resolve_backend(self.agent, thread_id="xyz")
        self.assertIn("状态异常", str(ctx.exception))

    def test_resolve_backend_calls_ensure_container_for_docker(self):
        """Docker 后端应调用 ensure_container"""
        with mock.patch("sandbox.backends.get_backend") as mock_get:
            mock_backend = mock.MagicMock(spec=["ensure_container"])
            mock_get.return_value = mock_backend
            resolve_backend(self.agent, thread_id="thread-001")
            mock_backend.ensure_container.assert_called_once()

    def test_resolve_backend_calls_ensure_dir_for_system(self):
        """System 后端应调用 ensure_dir"""
        with mock.patch("sandbox.backends.get_backend") as mock_get:
            mock_backend = mock.MagicMock(spec=["ensure_dir"])
            mock_get.return_value = mock_backend
            resolve_backend(self.agent, thread_id="thread-002")
            mock_backend.ensure_dir.assert_called_once()

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from core.common.exception.api_exception import ApiException
from agent.services.sandbox_resolver import resolve_backend
from agent.models import ElAgent


class TestResolveBackend:
    """resolve_backend 函数测试"""

    def test_with_sandbox_instance_id(self):
        """有 sandbox_instance_id 时，应调用 get_backend"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {"sandbox_instance_id": "sandbox-001"}

        mock_instance = MagicMock()
        mock_backend = MagicMock()

        with patch("sandbox.models.ElSandboxInstance") as mock_model:
            mock_model.objects.get.return_value = mock_instance
            with patch("sandbox.backends.get_backend") as mock_get:
                mock_get.return_value = mock_backend

                result = resolve_backend(agent_config)

                mock_model.objects.get.assert_called_once_with(id="sandbox-001")
                mock_get.assert_called_once_with(mock_instance)
                assert result is mock_backend

    def test_without_sandbox_instance_id_raises(self):
        """无 sandbox_instance_id 时，应抛出 ApiException"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {}

        with pytest.raises(ApiException) as exc_info:
            resolve_backend(agent_config)

        assert "未配置沙箱实例" in str(exc_info.value)
        assert "test-agent" in str(exc_info.value)

    def test_ensure_dir_called_for_system_backend(self):
        """系统后端应调用 ensure_dir"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {"sandbox_instance_id": "sandbox-001"}

        mock_instance = MagicMock()
        mock_backend = MagicMock()
        mock_backend.ensure_dir = MagicMock()
        # 确保没有 ensure_container 属性
        del mock_backend.ensure_container

        with patch("sandbox.models.ElSandboxInstance") as mock_model:
            mock_model.objects.get.return_value = mock_instance
            with patch("sandbox.backends.get_backend", return_value=mock_backend):
                result = resolve_backend(agent_config)

                mock_backend.ensure_dir.assert_called_once()
                assert result is mock_backend

    def test_ensure_container_called_for_docker_backend(self):
        """Docker 后端应调用 ensure_container"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {"sandbox_instance_id": "sandbox-001"}

        mock_instance = MagicMock()
        mock_backend = MagicMock()
        mock_backend.ensure_container = MagicMock()
        # 确保没有 ensure_dir 属性
        del mock_backend.ensure_dir

        with patch("sandbox.models.ElSandboxInstance") as mock_model:
            mock_model.objects.get.return_value = mock_instance
            with patch("sandbox.backends.get_backend", return_value=mock_backend):
                result = resolve_backend(agent_config)

                mock_backend.ensure_container.assert_called_once()
                assert result is mock_backend

    def test_ensure_dir_failure_does_not_block(self):
        """ensure_dir 失败不应阻塞后端返回"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {"sandbox_instance_id": "sandbox-001"}

        mock_instance = MagicMock()
        mock_backend = MagicMock()
        mock_backend.ensure_dir = MagicMock(side_effect=RuntimeError("dir failed"))

        with patch("sandbox.models.ElSandboxInstance") as mock_model:
            mock_model.objects.get.return_value = mock_instance
            with patch("sandbox.backends.get_backend", return_value=mock_backend):
                result = resolve_backend(agent_config)

                # 后端仍应被返回
                assert result is mock_backend

    def test_ensure_container_failure_does_not_block(self):
        """ensure_container 失败不应阻塞后端返回"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.name = "test-agent"
        agent_config.id = "agent-001"
        agent_config.metadata = {"sandbox_instance_id": "sandbox-001"}

        mock_instance = MagicMock()
        mock_backend = MagicMock()
        mock_backend.ensure_container = MagicMock(
            side_effect=RuntimeError("container failed")
        )

        with patch("sandbox.models.ElSandboxInstance") as mock_model:
            mock_model.objects.get.return_value = mock_instance
            with patch("sandbox.backends.get_backend", return_value=mock_backend):
                result = resolve_backend(agent_config)

                assert result is mock_backend

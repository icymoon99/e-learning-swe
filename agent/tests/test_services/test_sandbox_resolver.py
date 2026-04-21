from __future__ import annotations

from unittest.mock import MagicMock, patch

from agent.services.sandbox_resolver import resolve_backend
from agent.models import ElAgent


class TestResolveBackend:
    """resolve_backend 函数测试"""

    def test_with_sandbox_instance_id(self):
        """有 sandbox_instance_id 时，应调用 get_backend"""
        agent_config = MagicMock(spec=ElAgent)
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

    def test_without_sandbox_instance_id_defaults_to_local(self):
        """无 sandbox_instance_id 时，应返回 LocalSystemBackend"""
        agent_config = MagicMock(spec=ElAgent)
        agent_config.metadata = {}

        with patch(
            "sandbox.backends.local_system.LocalSystemBackend"
        ) as mock_local:
            mock_backend = MagicMock()
            mock_local.return_value = mock_backend

            result = resolve_backend(agent_config)

            mock_local.assert_called_once_with(
                name="default", root_path="/workspace"
            )
            assert result is mock_backend

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from core.common.exception.api_exception import ApiException
from agent.services.sandbox_resolver import resolve_backend
from agent.models import ElAgent
from sandbox.models import ElSandboxInstance


def _make_agent(sandbox):
    agent = MagicMock(spec=ElAgent)
    agent.name = "test-agent"
    agent.id = "agent-001"
    agent.sandbox_instance = sandbox
    return agent


class TestResolveBackend:
    """resolve_backend 使用 FK 取实例 + 状态检查"""

    def test_active_sandbox_returns_backend(self):
        """沙箱 active 时正常返回 backend"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "active"
        sandbox.metadata = {"image": "test:latest", "work_dir": "/workspace",
                            "ssh_host": "127.0.0.1", "ssh_port": 22,
                            "ssh_user": "root", "ssh_password": "test"}
        agent = _make_agent(sandbox)

        mock_backend = MagicMock()
        with patch("sandbox.backends.get_backend", return_value=mock_backend):
            result = resolve_backend(agent)

        assert result is mock_backend

    def test_inactive_sandbox_raises(self):
        """沙箱 inactive 时抛异常"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "inactive"
        sandbox.name = "未启动沙箱"
        agent = _make_agent(sandbox)

        with pytest.raises(ApiException) as exc_info:
            resolve_backend(agent)

        assert "未启动" in str(exc_info.value)

    def test_error_sandbox_raises(self):
        """沙箱 error 时抛异常"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "error"
        sandbox.name = "异常沙箱"
        agent = _make_agent(sandbox)

        with pytest.raises(ApiException) as exc_info:
            resolve_backend(agent)

        assert "异常" in str(exc_info.value)

    def test_ensure_dir_called_for_system_backend(self):
        """系统后端应调用 ensure_dir"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "active"
        sandbox.metadata = {"image": "test:latest", "work_dir": "/workspace",
                            "ssh_host": "127.0.0.1", "ssh_port": 22,
                            "ssh_user": "root", "ssh_password": "test"}
        agent = _make_agent(sandbox)

        mock_backend = MagicMock()
        mock_backend.ensure_dir = MagicMock()
        del mock_backend.ensure_container

        with patch("sandbox.backends.get_backend", return_value=mock_backend):
            result = resolve_backend(agent)

        mock_backend.ensure_dir.assert_called_once()
        assert result is mock_backend

    def test_ensure_container_called_for_docker_backend(self):
        """Docker 后端应调用 ensure_container"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "active"
        sandbox.metadata = {"image": "test:latest", "work_dir": "/workspace",
                            "ssh_host": "127.0.0.1", "ssh_port": 22,
                            "ssh_user": "root", "ssh_password": "test"}
        agent = _make_agent(sandbox)

        mock_backend = MagicMock()
        mock_backend.ensure_container = MagicMock()
        del mock_backend.ensure_dir

        with patch("sandbox.backends.get_backend", return_value=mock_backend):
            result = resolve_backend(agent)

        mock_backend.ensure_container.assert_called_once()
        assert result is mock_backend

    def test_ensure_dir_failure_does_not_block(self):
        """ensure_dir 失败不阻塞后端返回"""
        sandbox = MagicMock(spec=ElSandboxInstance)
        sandbox.status = "active"
        sandbox.metadata = {"image": "test:latest", "work_dir": "/workspace",
                            "ssh_host": "127.0.0.1", "ssh_port": 22,
                            "ssh_user": "root", "ssh_password": "test"}
        agent = _make_agent(sandbox)

        mock_backend = MagicMock()
        mock_backend.ensure_dir = MagicMock(side_effect=RuntimeError("failed"))

        with patch("sandbox.backends.get_backend", return_value=mock_backend):
            result = resolve_backend(agent)

        assert result is mock_backend

"""根据 Agent 配置解析沙箱后端。"""

from __future__ import annotations

import logging

from core.common.exception.api_exception import ApiException

from agent.models import ElAgent

logger = logging.getLogger(__name__)


def resolve_backend(agent_config: ElAgent, *, thread_id: str = ""):
    """从 Agent FK 字段解析沙箱后端。

    Args:
        agent_config: Agent 配置模型实例
        thread_id: 线程标识，用于沙箱工作目录隔离

    Returns:
        SandboxBackendProtocol 实现

    Raises:
        ApiException: 沙箱未配置、未启动或状态异常
    """
    from sandbox.backends import get_backend

    instance = agent_config.sandbox_instance

    if instance is None:
        raise ApiException(
            msg=f"Agent '{agent_config.name}' (id={agent_config.id}) 未配置沙箱实例"
        )

    if instance.status == "inactive":
        raise ApiException(
            msg=f"Agent '{agent_config.name}' 绑定的沙箱 '{instance.name}' 未启动，请先在沙箱管理中启动"
        )

    if instance.status == "error":
        raise ApiException(
            msg=f"Agent '{agent_config.name}' 绑定的沙箱 '{instance.name}' 状态异常，请检查"
        )

    backend = get_backend(instance, thread_id=thread_id)

    if hasattr(backend, "ensure_container"):
        try:
            backend.ensure_container()
        except Exception as e:
            logger.warning("沙箱容器初始化失败: %s", e)
    elif hasattr(backend, "ensure_dir"):
        try:
            backend.ensure_dir()
        except Exception as e:
            logger.warning("沙箱目录创建失败: %s", e)

    return backend

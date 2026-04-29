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

    logger.info("resolve_backend: 开始解析沙箱后端, agent=%s, thread_id=%s", agent_config.code, thread_id or "none")

    instance = agent_config.sandbox_instance

    if instance is None:
        logger.error("resolve_backend: Agent '%s' (id=%s) 未配置沙箱实例", agent_config.name, agent_config.id)
        raise ApiException(
            msg=f"Agent '{agent_config.name}' (id={agent_config.id}) 未配置沙箱实例"
        )

    if instance.status == "inactive":
        logger.error("resolve_backend: 沙箱 '%s' 未启动", instance.name)
        raise ApiException(
            msg=f"Agent '{agent_config.name}' 绑定的沙箱 '{instance.name}' 未启动，请先在沙箱管理中启动"
        )

    if instance.status == "error":
        logger.error("resolve_backend: 沙箱 '%s' 状态异常", instance.name)
        raise ApiException(
            msg=f"Agent '{agent_config.name}' 绑定的沙箱 '{instance.name}' 状态异常，请检查"
        )

    backend = get_backend(instance, thread_id=thread_id)
    logger.info("resolve_backend: 沙箱后端已创建, type=%s, work_dir=%s", type(backend).__name__, getattr(backend, "_work_dir", "N/A"))

    if hasattr(backend, "ensure_container"):
        try:
            backend.ensure_container()
            logger.info("resolve_backend: 沙箱容器初始化成功")
        except Exception as e:
            logger.warning("resolve_backend: 沙箱容器初始化失败: %s", e)
    elif hasattr(backend, "ensure_dir"):
        try:
            backend.ensure_dir()
            logger.info("resolve_backend: 沙箱目录已创建")
        except Exception as e:
            logger.warning("resolve_backend: 沙箱目录创建失败: %s", e)

    return backend

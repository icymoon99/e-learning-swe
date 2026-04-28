"""根据 Agent 配置解析沙箱后端。

任务模块尚未实现时，这里从 Agent metadata 中读取后端配置。
"""

from __future__ import annotations

from core.common.exception.api_exception import ApiException

from agent.models import ElAgent


def resolve_backend(agent_config: ElAgent):
    """从 Agent 配置中解析沙箱后端。

    Args:
        agent_config: Agent 配置模型实例

    Returns:
        SandboxBackendProtocol 实现
    """
    from sandbox.backends import get_backend
    from sandbox.models import ElSandboxInstance

    metadata = agent_config.metadata
    sandbox_id = metadata.get("sandbox_instance_id")

    if sandbox_id:
        instance = ElSandboxInstance.objects.get(id=sandbox_id)
        return get_backend(instance)

    raise ApiException(
        msg=f"Agent '{agent_config.name}' (id={agent_config.id}) 未配置沙箱实例，请在 Agent metadata 中设置 sandbox_instance_id"
    )

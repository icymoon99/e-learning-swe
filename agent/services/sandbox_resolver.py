"""根据 Agent 配置解析沙箱后端。

任务模块尚未实现时，这里从 Agent metadata 中读取后端配置。
"""

from __future__ import annotations

from agent.models import ElAgent


def resolve_backend(agent_config: ElAgent):
    """从 Agent 配置中解析沙箱后端。

    Args:
        agent_config: Agent 配置模型实例

    Returns:
        SandboxBackendProtocol 实现
    """
    from sandbox.backends import get_backend
    from sandbox.backends.local_system import LocalSystemBackend
    from sandbox.models import ElSandboxInstance

    metadata = agent_config.metadata
    sandbox_id = metadata.get("sandbox_instance_id")

    if sandbox_id:
        instance = ElSandboxInstance.objects.get(id=sandbox_id)
        return get_backend(instance)

    # 默认返回本地系统后端
    return LocalSystemBackend(name="default", root_path="/tmp", work_dir="/workspace")

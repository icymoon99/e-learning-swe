"""沙箱生命周期管理服务"""

import logging
import shlex
import subprocess

from sandbox.backends import get_backend
from sandbox.executors import SSHConfig, execute_remote
from sandbox.models import ElSandboxInstance

logger = logging.getLogger(__name__)


class SandboxService:
    """沙箱服务 — 封装启动/停止/重置/获取后端等高频操作"""

    def start(self, instance: ElSandboxInstance) -> None:
        """启动沙箱"""
        backend = get_backend(instance)
        if hasattr(backend, "ensure_container"):
            backend.ensure_container()
        elif hasattr(backend, "ensure_dir"):
            backend.ensure_dir()
        instance.status = "active"
        instance.save(update_fields=["status"])
        logger.info("[Sandbox] 沙箱已启动: %s", instance.name)

    def stop(self, instance: ElSandboxInstance) -> None:
        """停止沙箱"""
        if instance.type in ("localdocker", "remotedocker"):
            container_name = f"sandbox-{instance.id}"
            if instance.type == "localdocker":
                subprocess.run(
                    ["docker", "stop", container_name],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                metadata = instance.metadata
                ssh_config = SSHConfig(
                    host=metadata["ssh_host"],
                    port=metadata.get("ssh_port", 22),
                    user=metadata.get("ssh_user", ""),
                    key_path=metadata.get("ssh_key_path_enc", ""),
                )
                execute_remote(
                    f"docker stop {shlex.quote(container_name)}",
                    ssh_config,
                    timeout=30,
                )

        instance.status = "inactive"
        instance.save(update_fields=["status"])
        logger.info("[Sandbox] 沙箱已停止: %s", instance.name)

    def reset(self, instance: ElSandboxInstance) -> None:
        """重置沙箱（清空工作目录）"""
        backend = get_backend(instance)
        backend.reset()
        logger.info("[Sandbox] 沙箱已重置: %s", instance.name)

    def get_backend(self, instance: ElSandboxInstance):
        """获取沙箱后端实例"""
        return get_backend(instance)

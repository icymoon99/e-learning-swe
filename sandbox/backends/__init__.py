"""沙箱后端层 — 工厂函数 + 4 种具体后端"""

import os

from sandbox.backends.base import BaseSandboxBackend
from sandbox.backends.local_docker import LocalDockerBackend
from sandbox.backends.local_system import LocalSystemBackend
from sandbox.backends.remote_docker import RemoteDockerBackend
from sandbox.backends.remote_system import RemoteSystemBackend
from sandbox.executors import SSHConfig
from sandbox.models import ElSandboxInstance

__all__ = [
    "BaseSandboxBackend",
    "LocalDockerBackend",
    "RemoteDockerBackend",
    "LocalSystemBackend",
    "RemoteSystemBackend",
    "get_backend",
]


def get_backend(instance: ElSandboxInstance, thread_id: str = ""):
    """根据沙箱实例创建并返回对应后端

    Args:
        instance: ElSandboxInstance 模型实例
        thread_id: 可选的线程 ID，传入时自动为 work_dir 追加隔离后缀

    Returns:
        对应类型的 SandboxBackendProtocol 实现
    """
    metadata = instance.metadata
    base_work_dir = metadata.get("work_dir", "workspace")

    # 隔离：追加 thread_id 后缀
    isolated_work_dir = f"{base_work_dir}-{thread_id}" if thread_id else base_work_dir

    if instance.type == "localdocker":
        container_name = f"sandbox-{instance.id}"
        return LocalDockerBackend(
            container_name=container_name,
            image=metadata.get("image", "sandbox:latest"),
            work_dir=isolated_work_dir,
        )

    elif instance.type == "remotedocker":
        from core.common.utils.aes_utils import aes_decrypt_with_key

        container_name = f"sandbox-{instance.id}"
        ssh_key_path = metadata.get("ssh_key_path_enc", "")
        if ssh_key_path:
            key = os.getenv("SANDBOX_AES_KEY", "").encode()
            iv = os.getenv("SANDBOX_AES_IV", "").encode()
            ssh_key_path = aes_decrypt_with_key(ssh_key_path, key, iv)

        ssh_config = SSHConfig(
            host=metadata["ssh_host"],
            port=metadata.get("ssh_port", 22),
            user=metadata.get("ssh_user", ""),
            key_path=ssh_key_path,
        )
        return RemoteDockerBackend(
            container_name=container_name,
            ssh_config=ssh_config,
            image=metadata.get("image", "sandbox:latest"),
            work_dir=isolated_work_dir,
        )

    elif instance.type == "localsystem":
        return LocalSystemBackend(
            name=instance.name,
            root_path=metadata.get("root_path", "sandbox/"),
            work_dir=isolated_work_dir,
        )

    elif instance.type == "remotesystem":
        from core.common.utils.aes_utils import aes_decrypt_with_key

        ssh_password = metadata.get("ssh_password_enc", "")
        ssh_key_path = metadata.get("ssh_key_path_enc", "")
        key = os.getenv("SANDBOX_AES_KEY", "").encode()
        iv = os.getenv("SANDBOX_AES_IV", "").encode()

        if ssh_password:
            ssh_password = aes_decrypt_with_key(ssh_password, key, iv)
        if ssh_key_path:
            ssh_key_path = aes_decrypt_with_key(ssh_key_path, key, iv)

        ssh_config = SSHConfig(
            host=metadata["ssh_host"],
            port=metadata.get("ssh_port", 22),
            user=metadata.get("ssh_user", ""),
            key_path=ssh_key_path,
            password=ssh_password,
        )
        return RemoteSystemBackend(
            name=instance.name,
            root_path=metadata.get("root_path", "sandbox/"),
            work_dir=isolated_work_dir,
            ssh_config=ssh_config,
        )

    raise ValueError(f"Unknown sandbox type: {instance.type}")

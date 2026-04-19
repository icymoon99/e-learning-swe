"""SSH 远程执行器"""
import subprocess
from dataclasses import dataclass

from sandbox.executors.data import ExecResult


@dataclass
class SSHConfig:
    """SSH 连接配置"""

    host: str
    port: int = 22
    user: str = ""
    key_path: str = ""
    password: str = ""


def execute_remote(cmd: str, ssh_config: SSHConfig, timeout: int = 300) -> ExecResult:
    """SSH 远程执行命令

    Args:
        cmd: 要在远程机器上执行的 shell 命令
        ssh_config: SSH 连接配置
        timeout: 超时时间（秒）

    Returns:
        ExecResult 包含 stdout, stderr, exit_code
    """
    ssh_cmd = ["ssh"]
    ssh_cmd.extend(["-p", str(ssh_config.port)])
    ssh_cmd.extend(["-o", "StrictHostKeyChecking=no"])
    ssh_cmd.extend(["-o", "ConnectTimeout=10"])
    if ssh_config.key_path:
        ssh_cmd.extend(["-i", ssh_config.key_path])

    user_host = (
        f"{ssh_config.user}@{ssh_config.host}"
        if ssh_config.user
        else ssh_config.host
    )
    ssh_cmd.append(user_host)
    ssh_cmd.append(cmd)

    result = subprocess.run(
        ssh_cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return ExecResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )

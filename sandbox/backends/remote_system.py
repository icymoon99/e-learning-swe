"""远程系统目录沙箱后端"""

import logging
import shlex

from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend
from sandbox.executors import SSHConfig, execute_remote

logger = logging.getLogger(__name__)


class RemoteSystemBackend(BaseSandboxBackend):
    """远程系统目录沙箱（通过 SSH 连接后在指定目录执行）"""

    def __init__(self, name: str, root_path: str, ssh_config: SSHConfig):
        self._name = name
        self._root_path = root_path
        self._ssh_config = ssh_config

    @property
    def id(self) -> str:
        return f"remote-system-{self._name}"

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"cd {shlex.quote(self._root_path)} && {inner_cmd}"

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        result = execute_remote(command, self._ssh_config, timeout=timeout or 300)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def ensure_dir(self) -> None:
        """确保远程根目录存在"""
        cmd = f"mkdir -p {shlex.quote(self._root_path)}"
        execute_remote(cmd, self._ssh_config)

    def reset(self) -> None:
        cmd = self._build_cmd(
            f"rm -rf {shlex.quote(self._root_path)}/* {shlex.quote(self._root_path)}/.* 2>/dev/null; mkdir -p {shlex.quote(self._root_path)}"
        )
        self.execute(cmd)

"""本地系统目录沙箱后端"""

import logging
import os
import shlex

from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend
from sandbox.executors import execute_local

logger = logging.getLogger(__name__)


class LocalSystemBackend(BaseSandboxBackend):
    """本地系统目录沙箱（直接在本地目录执行命令）"""

    def __init__(self, name: str, root_path: str):
        self._name = name
        self._root_path = root_path

    @property
    def id(self) -> str:
        return f"local-system-{self._name}"

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"cd {shlex.quote(self._root_path)} && {inner_cmd}"

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        result = execute_local(command, timeout=timeout or 300)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def ensure_dir(self) -> None:
        """确保根目录存在"""
        os.makedirs(self._root_path, exist_ok=True)

    def reset(self) -> None:
        """清空工作目录"""
        cmd = self._build_cmd(
            f"rm -rf {shlex.quote(self._root_path)}/* {shlex.quote(self._root_path)}/.* 2>/dev/null; mkdir -p {shlex.quote(self._root_path)}"
        )
        self.execute(cmd)

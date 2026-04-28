"""本地系统目录沙箱后端"""

import logging
import os
import shlex

from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend, _sanitize_env
from sandbox.executors import execute_local

logger = logging.getLogger(__name__)


class LocalSystemBackend(BaseSandboxBackend):
    """本地系统目录沙箱（直接在本地目录执行命令）"""

    def __init__(self, name: str, root_path: str, work_dir: str = "/workspace"):
        self._name = name
        self._root_path = root_path
        self._work_dir = work_dir

    @property
    def id(self) -> str:
        return f"local-system-{self._name}"

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"cd {shlex.quote(self._work_dir)} && {inner_cmd}"

    def execute(
        self, command: str, *, timeout: int | None = None, env: dict | None = None
    ) -> ExecuteResponse:
        safe_env = _sanitize_env(env) if env else None
        result = execute_local(command, timeout=timeout or 300, env=safe_env)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def ensure_dir(self) -> None:
        """确保工作目录存在"""
        os.makedirs(self._work_dir, exist_ok=True)

    def reset(self) -> None:
        """清空工作目录"""
        cmd = self._build_cmd(
            f"rm -rf {shlex.quote(self._work_dir)}/* {shlex.quote(self._work_dir)}/.* 2>/dev/null; mkdir -p {shlex.quote(self._work_dir)}"
        )
        self.execute(cmd)

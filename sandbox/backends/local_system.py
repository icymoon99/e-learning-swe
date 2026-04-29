"""本地系统目录沙箱后端"""

import logging
import os
import posixpath
import shlex

from core.common.exception.api_exception import ApiException
from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend, _sanitize_env
from sandbox.executors import execute_local

logger = logging.getLogger(__name__)


class LocalSystemBackend(BaseSandboxBackend):
    """本地系统目录沙箱（直接在本地目录执行命令）"""

    def __init__(self, name: str, root_path: str, work_dir: str = "workspace"):
        self._name = name
        self._root_path = root_path
        self._work_dir = work_dir

    @property
    def id(self) -> str:
        return f"local-system-{self._name}"

    def _full_dir(self) -> str:
        return posixpath.join(self._root_path, self._work_dir)

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"cd {shlex.quote(self._full_dir())} && {inner_cmd}"

    def execute(
        self, command: str, *, timeout: int | None = None, env: dict | None = None
    ) -> ExecuteResponse:
        safe_env = _sanitize_env(env) if env else None
        full_cmd = self._build_cmd(command)
        result = execute_local(full_cmd, timeout=timeout or 300, env=safe_env)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def ensure_dir(self) -> None:
        """确保工作目录存在"""
        os.makedirs(self._full_dir(), exist_ok=True)

    def reset(self) -> None:
        """清空工作目录"""
        full_dir = self._full_dir()
        cmd = f"cd {shlex.quote(full_dir)} && rm -rf ./* ./.* 2>/dev/null; mkdir -p {shlex.quote(full_dir)}"
        self.execute(cmd)

    def _validate_path(self, file_path: str) -> str:
        """校验文件路径必须在 work_dir 范围内，防止路径遍历攻击。"""
        full_dir = self._full_dir()
        real_path = posixpath.normpath(file_path)
        norm_dir = posixpath.normpath(full_dir)
        if not real_path.startswith(norm_dir + "/") and real_path != norm_dir:
            raise ApiException(
                msg=f"路径遍历被拒绝: {file_path} 超出工作目录 {full_dir}"
            )
        return real_path

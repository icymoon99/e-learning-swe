"""远程系统目录沙箱后端"""

import logging
import posixpath
import shlex

from core.common.exception.api_exception import ApiException
from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend, _sanitize_env
from sandbox.executors import SSHConfig, execute_remote

logger = logging.getLogger(__name__)


class RemoteSystemBackend(BaseSandboxBackend):
    """远程系统目录沙箱（通过 SSH 连接后在指定目录执行）"""

    def __init__(
        self, name: str, root_path: str, ssh_config: SSHConfig, work_dir: str = "workspace"
    ):
        self._name = name
        self._root_path = root_path
        self._work_dir = work_dir
        self._ssh_config = ssh_config

    @property
    def id(self) -> str:
        return f"remote-system-{self._name}"

    def _full_dir(self) -> str:
        return posixpath.join(self._root_path, self._work_dir)

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"cd {shlex.quote(self._full_dir())} && {inner_cmd}"

    def execute(
        self, command: str, *, timeout: int | None = None, env: dict | None = None
    ) -> ExecuteResponse:
        cmd_with_cd = self._build_cmd(command)
        full_cmd = self._build_cmd_with_env(cmd_with_cd, env)
        result = execute_remote(full_cmd, self._ssh_config, timeout=timeout or 300)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def _build_cmd_with_env(self, inner_cmd: str, env: dict | None = None) -> str:
        """构建 SSH 命令，使用 export 前缀传递环境变量。"""
        safe_env = _sanitize_env(env) if env else {}

        if safe_env:
            export_vars = " ".join(
                f"export {shlex.quote(key)}={shlex.quote(value)}"
                for key, value in safe_env.items()
            )
            return f"{export_vars} && {inner_cmd}"
        return inner_cmd

    def ensure_dir(self) -> None:
        """确保远程工作目录存在"""
        cmd = f"mkdir -p {shlex.quote(self._full_dir())}"
        execute_remote(cmd, self._ssh_config)

    def reset(self) -> None:
        """清空远程工作目录"""
        full_dir = self._full_dir()
        cmd = f"cd {shlex.quote(full_dir)} && rm -rf {shlex.quote(full_dir)}/* {shlex.quote(full_dir)}/.* 2>/dev/null; mkdir -p {shlex.quote(full_dir)}"
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

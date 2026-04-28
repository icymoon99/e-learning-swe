"""远程 Docker 沙箱后端"""

import logging
import shlex

from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend, _sanitize_env
from sandbox.executors import SSHConfig, execute_remote

logger = logging.getLogger(__name__)


class RemoteDockerBackend(BaseSandboxBackend):
    """远程 Docker 容器沙箱（通过 SSH 连接）"""

    def __init__(
        self,
        container_name: str,
        ssh_config: SSHConfig,
        image: str = "sandbox:latest",
        work_dir: str = "/workspace",
    ):
        self._container_name = container_name
        self._ssh_config = ssh_config
        self._image = image
        self._work_dir = work_dir

    @property
    def id(self) -> str:
        return self._container_name

    def _build_cmd(self, inner_cmd: str) -> str:
        escaped_inner = shlex.quote(f"cd {shlex.quote(self._work_dir)} && {inner_cmd}")
        return f"docker exec {self._container_name} bash -c {escaped_inner}"

    def execute(
        self, command: str, *, timeout: int | None = None, env: dict | None = None
    ) -> ExecuteResponse:
        full_cmd = self._build_cmd_with_env(command, env)
        result = execute_remote(full_cmd, self._ssh_config, timeout=timeout or 300)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def _build_cmd_with_env(self, inner_cmd: str, env: dict | None = None) -> str:
        """构建 docker exec 命令，包含环境变量。"""
        safe_env = _sanitize_env(env) if env else {}

        env_args = ""
        for key, value in safe_env.items():
            env_args += f" -e {shlex.quote(key)}={shlex.quote(value)}"

        escaped_inner = shlex.quote(f"cd {shlex.quote(self._work_dir)} && {inner_cmd}")
        return f"docker exec{env_args} {self._container_name} bash -c {escaped_inner}"

    def _remote_shell(self, cmd: str, timeout: int = 300) -> None:
        """在远程服务器上执行 shell 命令（非 docker exec）"""
        execute_remote(cmd, self._ssh_config, timeout=timeout)

    def ensure_container(self) -> None:
        """确保远程容器存在"""
        inspect_cmd = f"docker inspect {self._container_name} --format '{{{{.Id}}}}'"
        result = execute_remote(inspect_cmd, self._ssh_config, timeout=30)
        if result.exit_code == 0 and result.stdout.strip():
            logger.info("[Sandbox] 远程容器已存在: %s", self._container_name)
        else:
            docker_run = (
                f"docker run -d --name {self._container_name} --rm "
                f"-w {self._work_dir} {shlex.quote(self._image)} tail -f /dev/null"
            )
            result = execute_remote(docker_run, self._ssh_config, timeout=30)
            if result.exit_code != 0:
                raise RuntimeError(
                    f"Failed to create remote container: {result.stderr}"
                )

    def reset(self) -> None:
        cmd = self._build_cmd(
            f"rm -rf {self._work_dir}/* {self._work_dir}/.* 2>/dev/null; mkdir -p {self._work_dir}"
        )
        self.execute(cmd)

    def clone_repo(
        self,
        repo_url: str,
        token: str = "",
        branch: str = "",
        target_path: str = "/workspace",
    ) -> None:
        if branch:
            cmd = f"git clone --branch {shlex.quote(branch)} --single-branch {shlex.quote(repo_url)} {shlex.quote(target_path)}"
        else:
            cmd = f"git clone {shlex.quote(repo_url)} {shlex.quote(target_path)}"
        exec_cmd = self._build_cmd(cmd)
        result = execute_remote(exec_cmd, self._ssh_config, timeout=120)
        if result.exit_code != 0:
            raise RuntimeError(f"git clone failed: {result.stderr}")

    def checkout_branch(self, branch_name: str, create: bool = False) -> None:
        if create:
            cmd = f"git -C {self._work_dir} checkout -b {shlex.quote(branch_name)}"
        else:
            cmd = f"git -C {self._work_dir} checkout {shlex.quote(branch_name)}"
        exec_cmd = self._build_cmd(cmd)
        result = execute_remote(exec_cmd, self._ssh_config)
        if result.exit_code != 0:
            raise RuntimeError(f"git checkout failed: {result.stderr}")

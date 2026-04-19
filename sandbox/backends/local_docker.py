"""本地 Docker 沙箱后端"""

import logging
import shlex
import subprocess

from deepagents.backends.protocol import ExecuteResponse

from sandbox.backends.base import BaseSandboxBackend
from sandbox.executors import execute_local

logger = logging.getLogger(__name__)


class LocalDockerBackend(BaseSandboxBackend):
    """本地 Docker 容器沙箱"""

    def __init__(
        self,
        container_name: str,
        image: str = "sandbox:latest",
        work_dir: str = "/workspace",
    ):
        self._container_name = container_name
        self._image = image
        self._work_dir = work_dir

    @property
    def id(self) -> str:
        return self._container_name

    def _build_cmd(self, inner_cmd: str) -> str:
        return f"docker exec {self._container_name} bash -c {shlex.quote(inner_cmd)}"

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        result = execute_local(command, timeout=timeout or 300)
        output = result.stdout
        if result.stderr:
            output = output + result.stderr if output else result.stderr
        return ExecuteResponse(
            output=output, exit_code=result.exit_code, truncated=False
        )

    def ensure_container(self) -> None:
        """确保容器存在"""
        result = subprocess.run(
            ["docker", "inspect", self._container_name, "--format", "{{.Id}}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("[Sandbox] 容器已存在: %s", self._container_name)
        else:
            logger.info("[Sandbox] 创建容器: %s", self._container_name)
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                self._container_name,
                "--rm",
                "-w",
                self._work_dir,
            ]
            cmd.extend([self._image, "tail", "-f", "/dev/null"])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"Failed to create container: {result.stderr}")

    def reset(self) -> None:
        """清空工作目录"""
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
        """克隆代码库"""
        if branch:
            cmd = f"git clone --branch {shlex.quote(branch)} --single-branch {shlex.quote(repo_url)} {shlex.quote(target_path)}"
        else:
            cmd = f"git clone {shlex.quote(repo_url)} {shlex.quote(target_path)}"
        exec_cmd = self._build_cmd(cmd)
        result = execute_local(exec_cmd, timeout=120)
        if result.exit_code != 0:
            raise RuntimeError(f"git clone failed: {result.stderr}")

    def checkout_branch(self, branch_name: str, create: bool = False) -> None:
        """检出分支"""
        if create:
            cmd = f"git -C {self._work_dir} checkout -b {shlex.quote(branch_name)}"
        else:
            cmd = f"git -C {self._work_dir} checkout {shlex.quote(branch_name)}"
        exec_cmd = self._build_cmd(cmd)
        result = execute_local(exec_cmd)
        if result.exit_code != 0:
            raise RuntimeError(f"git checkout failed: {result.stderr}")

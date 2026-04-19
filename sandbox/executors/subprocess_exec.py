"""本地 subprocess 执行器"""
import subprocess

from sandbox.executors.data import ExecResult


def execute_local(cmd: str, timeout: int = 300) -> ExecResult:
    """本地执行命令

    Args:
        cmd: 要执行的 shell 命令
        timeout: 超时时间（秒）

    Returns:
        ExecResult 包含 stdout, stderr, exit_code
    """
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return ExecResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )

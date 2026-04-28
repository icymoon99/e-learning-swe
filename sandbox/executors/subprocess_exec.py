"""本地 subprocess 执行器"""
import os
import subprocess

from sandbox.executors.data import ExecResult


def execute_local(cmd: str, timeout: int = 300, env: dict | None = None) -> ExecResult:
    """本地执行命令

    Args:
        cmd: 要执行的 shell 命令
        timeout: 超时时间（秒）
        env: 可选的环境变量字典，会与系统环境变量合并

    Returns:
        ExecResult 包含 stdout, stderr, exit_code
    """
    run_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=run_env,
    )
    return ExecResult(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.returncode,
    )

"""沙箱执行传输层 — 本地 subprocess + SSH 远程执行"""
from sandbox.executors.data import ExecResult
from sandbox.executors.subprocess_exec import execute_local
from sandbox.executors.ssh_exec import SSHConfig, execute_remote

__all__ = ["ExecResult", "SSHConfig", "execute_local", "execute_remote"]

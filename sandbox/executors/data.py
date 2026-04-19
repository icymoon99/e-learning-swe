"""沙箱执行传输层 — 数据结构定义"""
from dataclasses import dataclass


@dataclass
class ExecResult:
    """统一执行结果"""

    stdout: str
    stderr: str
    exit_code: int

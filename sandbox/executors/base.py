"""CLI 执行器抽象基类与注册表"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExecutorResult:
    """CLI 执行器解析后的结果"""

    success: bool
    session_id: str | None
    output: str
    files_changed: list[str] = field(default_factory=list)
    error: str | None = None


class CLIExecutor(ABC):
    """CLI 执行器抽象基类。

    子类必须实现：
    - code: 执行器唯一标识（如 'trae'）
    - name: 显示名称（如 'Trae CLI'）
    - build_command(query, session_id, work_dir, **kwargs)
    - parse_output(raw_output)
    """

    code: str
    name: str

    @abstractmethod
    def build_command(
        self, query: str, session_id: str | None = None, *,
        work_dir: str = '/workspace', **kwargs
    ) -> list[str]:
        """构建 CLI 命令列表（不拼接为字符串）"""

    @abstractmethod
    def parse_output(self, raw_output: str) -> ExecutorResult:
        """解析 CLI 标准输出"""


class ExecutorRegistry:
    """CLI 执行器注册表（进程级单例）"""

    _registry: dict[str, CLIExecutor] = {}

    @classmethod
    def register(cls, executor: CLIExecutor) -> None:
        cls._registry[executor.code] = executor

    @classmethod
    def get(cls, code: str) -> CLIExecutor:
        if code not in cls._registry:
            raise KeyError(f"CLI 执行器未注册: {code}")
        return cls._registry[code]

    @classmethod
    def list_all(cls) -> list[CLIExecutor]:
        return list(cls._registry.values())

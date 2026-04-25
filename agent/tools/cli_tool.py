"""LangChain Tool 工厂 — 将 CLI 执行器封装为 Agent 可调用的工具"""
from __future__ import annotations

import logging
import shlex
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from sandbox.executors.base import CLIExecutor, ExecutorRegistry

logger = logging.getLogger(__name__)


def create_cli_tool(
    executor_code: str,
    backend: Any,
    timeout: int = 3600,
):
    """创建 LangChain CLI 执行器 Tool。

    Args:
        executor_code: 执行器标识（如 'trae'）
        backend: 沙箱后端实例，用于 execute()
        timeout: 执行超时（秒）

    Returns:
        LangChain Tool 实例
    """
    executor = ExecutorRegistry.get(executor_code)

    class ToolInput(BaseModel):
        query: str = Field(description='给 CLI 工具的指令/任务描述')
        session_id: str | None = Field(
            default=None,
            description='可选：恢复之前的 CLI 会话 ID',
        )

    @tool('code_workshop', args_schema=ToolInput)
    def code_workshop(query: str, session_id: str | None = None) -> str:
        """调用沙箱内的专用编程工具（如 Trae CLI）完成编码或文档任务。

        适用于：新功能实现、代码重构、Bug 修复、文档撰写、测试编写等。
        该工具会在沙箱内启动一个带上下文感知的编程 Agent，
        自动完成代码/文档修改，完成后返回变更的文件列表和总结。
        如需人工确认的操作（如 git commit），该工具会自动跳过。
        """
        cmd_parts = executor.build_command(
            query=query, session_id=session_id, timeout=timeout,
        )
        cmd_str = shlex.join(cmd_parts)

        result = backend.execute(cmd_str, timeout=timeout)

        parsed = executor.parse_output(result.output)

        if parsed.success:
            changed = ', '.join(parsed.files_changed) if parsed.files_changed else '无文件变更'
            return f'CLI 执行成功。\n文件变更: {changed}\n输出: {parsed.output}'
        else:
            return f'CLI 执行失败: {parsed.error}'

    return code_workshop

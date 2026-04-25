"""Trae CLI 执行器插件"""
from __future__ import annotations

import json
import logging
import re
import uuid

from sandbox.executors.base import CLIExecutor, ExecutorResult

logger = logging.getLogger(__name__)

TRAEOCL_DEFAULT_TIMEOUT = 3600

# Query 后缀模板，追加到用户指令末尾
TRAEOCL_QUERY_SUFFIX = (
    "\n\n【重要】完成工作后，请在回复的最后输出一个 JSON 块，"
    "格式如下（仅输出该 JSON 块，不要其他内容）：\n"
    "```json\n"
    "{\n"
    '  "summary": "完成工作的简要中文总结",\n'
    '  "files_changed": ["path/to/file1", "path/to/file2"],\n'
    '  "status": "success"\n'
    '}\n'
    "```\n"
    "如果任务无法完成，请将 status 设为 \"error\" 并在 summary 中说明原因。"
)


class TraeExecutor(CLIExecutor):
    code = 'trae'
    name = 'Trae CLI'

    def build_command(
        self, query: str, session_id: str | None = None, *,
        work_dir: str = '/workspace', timeout: int = TRAEOCL_DEFAULT_TIMEOUT, **kwargs
    ) -> list[str]:
        # 改写 query：追加 JSON 格式约束
        wrapped_query = f"{query}\n{TRAEOCL_QUERY_SUFFIX}"

        cmd = ['traecli']

        # 会话管理：恢复 or 新建
        if session_id:
            cmd.extend(['--resume', session_id])
        else:
            cmd.extend(['--session-id', f'task-{uuid.uuid4().hex[:8]}'])

        cmd.extend([
            '--yolo',
            '--json',
            '--print',
            '--query-timeout', str(timeout),
            '--query', wrapped_query,
        ])

        return cmd

    def parse_output(self, raw_output: str) -> ExecutorResult:
        """解析 Trae CLI 输出。

        需要处理两层结构：
        1. CLI 自身可能输出 JSON 包装（--json 模式）
        2. LLM 回复中包含约定格式的 ```json ... ``` 块
        """
        # 先尝试从 LLM 回复中提取 ```json ... ``` 块
        json_match = re.search(r'```json\s*\n(.*?)\n```', raw_output, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ExecutorResult(
                    success=data.get('status') == 'success',
                    session_id=data.get('session_id'),
                    output=data.get('summary', ''),
                    files_changed=data.get('files_changed', []),
                    error=None if data.get('status') == 'success' else data.get('summary'),
                )
            except json.JSONDecodeError:
                logger.warning("从 query 约束的 JSON 块解析失败")

        # 退路：尝试解析整个输出为 CLI 自身 JSON
        try:
            data = json.loads(raw_output)
            return ExecutorResult(
                success=data.get('status') == 'success',
                session_id=data.get('session_id'),
                output=data.get('message', raw_output),
                files_changed=data.get('files_changed', []),
                error=data.get('error'),
            )
        except json.JSONDecodeError:
            return ExecutorResult(
                success=False, session_id=None,
                output=raw_output, error='无法解析执行结果'
            )

"""任务级记忆中间件 — 在 Agent 执行前后读写历史记忆。

before_agent: 读取历史记忆，注入系统提示词（超阈值时调用 LLM 摘要）
after_agent:  解析 Agent 输出，保存本次执行结果到 ElTaskMemory
"""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from task.models import ElTaskMemory
from agent.models import ElAgent
from task.services.memory_summarizer import MemorySummarizer, estimate_tokens as estimate_tokens_fn

logger = logging.getLogger(__name__)


class TaskMemoryMiddleware(AgentMiddleware):
    """任务级记忆中间件

    注意：before_agent / after_agent 必须为同步方法，
    LangGraph 的 AgentMiddleware 不支持异步钩子。
    """

    MEMORY_TOKEN_LIMIT = 8000  # 记忆注入的 token 上限

    def __init__(self, task_id: str, agent_code: str = ""):
        from agent.models import ElAgent

        self.task_id = task_id
        self._agent_code = agent_code  # 保存供 after_agent 使用
        self.summarizer = MemorySummarizer()

        # 根据 agent_code 获取 LLM 模型
        if agent_code:
            try:
                agent = ElAgent.objects.get(code=agent_code)
                if agent.llm_model:
                    self.summarizer = MemorySummarizer(
                        token_limit=self.MEMORY_TOKEN_LIMIT,
                        llm_model=agent.llm_model,
                    )
            except ElAgent.DoesNotExist:
                logger.warning(
                    "TaskMemoryMiddleware: Agent(code=%s) 不存在，使用默认摘要服务",
                    agent_code,
                )

        self.summarizer.token_limit = self.MEMORY_TOKEN_LIMIT

    def before_agent(self, state: dict, runtime: Runtime) -> dict[str, Any] | None:
        """读取历史记忆，注入到系统提示词。"""
        memories = self._get_memories()

        if not memories:
            logger.debug("TaskMemoryMiddleware: 无历史记忆，跳过")
            return None

        # 格式化为结构化文本
        full_text = self._format_memories(memories)

        # 判断是否需要摘要
        if self._estimate_tokens(full_text) <= self.MEMORY_TOKEN_LIMIT:
            memory_context = full_text
        else:
            logger.info(
                "TaskMemoryMiddleware: 记忆超过阈值 (%d tokens)，触发摘要",
                self._estimate_tokens(full_text),
            )
            memory_context = self._summarize_memories(memories)

        # 注入到系统提示词
        current_prompt = state.get("system_prompt", "")
        state["system_prompt"] = f"{current_prompt}\n\n## 任务历史记忆\n{memory_context}"
        logger.info("TaskMemoryMiddleware: 历史记忆已注入到系统提示词")
        return None

    def after_agent(
        self, state: dict, runtime: Runtime, *, success: bool = True
    ) -> dict[str, Any] | None:
        """解析 Agent 输出，保存本次执行结果到 ElTaskMemory。"""
        agent_code = self._agent_code or "unknown"

        # 获取 Agent 实例（用于记录）
        agent = None
        try:
            agent = ElAgent.objects.get(code=agent_code)
        except ElAgent.DoesNotExist:
            logger.warning("TaskMemoryMiddleware: Agent(code=%s) 不存在", agent_code)

        # 获取 thread_id
        thread_id = ""
        if hasattr(runtime, "context") and runtime.context:
            thread_id = getattr(runtime.context, "thread_id", "")

        # 从 state 中提取 GitSandboxMiddleware 的结果
        git_pr_url = state.get("git_pr_url")
        git_commit_hash = state.get("git_commit_hash")

        # 解析 Agent 输出
        summary, commit_message = self._parse_agent_output(state)

        # 判断执行状态
        error_message = state.get("error_message") if not success else None

        # 计算 execution_order
        count = ElTaskMemory.objects.filter(task_id=self.task_id).count()
        order = count + 1

        # 创建记忆记录
        ElTaskMemory.objects.create(
            task_id=self.task_id,
            agent=agent,
            thread_id=thread_id,
            execution_order=order,
            summary=summary,
            commit_message=commit_message,
            pr_url=git_pr_url,
            commit_hash=git_commit_hash,
            status="success" if success else "failed",
            error_message=error_message,
        )

        logger.info(
            "TaskMemoryMiddleware: 记忆已保存 (task=%s, order=%d)", self.task_id, order
        )
        return None

    # ------------------------------------------------------------------ #
    # 内部方法
    # ------------------------------------------------------------------ #

    def _get_memories(self):
        """查询成功的历史记忆。"""
        return list(
            ElTaskMemory.objects.filter(
                task_id=self.task_id,
                status="success",
            ).order_by("execution_order")
        )

    def _format_memories(self, memories) -> str:
        """将记忆格式化为结构化文本。"""
        lines = []
        for m in memories:
            agent_name = m.agent.name if m.agent else "unknown"
            lines.append(f"[第{m.execution_order}步 - {agent_name}]")
            lines.append(f"摘要：{m.summary}")
            if m.commit_message:
                lines.append(f"提交信息：{m.commit_message}")
            if m.pr_url:
                lines.append(f"PR：{m.pr_url}")
            if m.error_message:
                lines.append(f"错误：{m.error_message}")
            lines.append("")  # 空行分隔
        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """估算 token 数。"""
        return estimate_tokens_fn(text)

    def _summarize_memories(self, memories) -> str:
        """调用轻量 LLM 对历史记忆进行总结。"""
        full_text = self._format_memories(memories)
        return self.summarizer.summarize(full_text)

    def _parse_agent_output(self, state: dict) -> tuple[str, str]:
        """从 Agent state 中解析 summary 和 commit_message。"""
        default_summary = "Agent 完成工作"
        default_commit = "feat: agent 完成工作"

        try:
            # 尝试从 agent_output 中直接获取
            agent_output = state.get("agent_output", {})
            if agent_output and isinstance(agent_output, dict):
                return (
                    agent_output.get("summary", default_summary),
                    agent_output.get("commit_message", default_commit),
                )

            # 尝试从 messages 中解析 JSON
            messages = state.get("messages", [])
            if not messages:
                return default_summary, default_commit

            last_ai_msg = None
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    last_ai_msg = msg
                    break

            if last_ai_msg is None:
                return default_summary, default_commit

            content = last_ai_msg.content
            if "```" in content:
                for block in content.split("```"):
                    block = block.strip()
                    if block.startswith("json"):
                        block = block[4:].strip()
                    if block.startswith("{"):
                        data = json.loads(block)
                        return (
                            data.get("summary", default_summary),
                            data.get("commit_message", default_commit),
                        )

            if content.strip().startswith("{"):
                data = json.loads(content)
                return (
                    data.get("summary", default_summary),
                    data.get("commit_message", default_commit),
                )

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning("TaskMemoryMiddleware: 无法解析 Agent 输出: %s", e)

        return default_summary, default_commit

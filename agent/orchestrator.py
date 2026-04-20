"""
Agent 编排器

全局单例，负责：
- 缓存已编译的 Agent 实例（CompiledStateGraph）
- 提供 execute() 入口供 Django-Q2 任务调用
- 同步收集执行事件，写入执行日志
"""
from __future__ import annotations

import logging
from threading import Lock
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent

from agent.models import ElAgent, ElAgentExecutionLog

logger = logging.getLogger(__name__)


class Orchestrator:
    """Agent 编排器（全局单例）"""

    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}  # agent_id -> CompiledStateGraph
        self._lock = Lock()

    def get_or_create_agent(self, agent_id: str) -> Any:
        """获取或创建 Agent 实例（线程安全）"""
        with self._lock:
            if agent_id not in self._agents:
                self._agents[agent_id] = self._build_agent(agent_id)
            return self._agents[agent_id]

    def _build_agent(self, agent_id: str) -> Any:
        """根据 Agent 配置创建 deep agent 实例"""
        agent_config = ElAgent.objects.get(id=agent_id)

        llm = ChatOpenAI(model=agent_config.model)
        checkpointer = MemorySaver()

        agent = create_deep_agent(
            model=llm,
            system_prompt=agent_config.system_prompt,
            checkpointer=checkpointer,
        )

        logger.info("Agent 实例已创建: %s (id=%s)", agent_config.code, agent_id)
        return agent

    def execute(
        self,
        agent_id: str,
        message: str,
        thread_id: str,
    ) -> dict[str, Any]:
        """
        执行 Agent 任务（同步阻塞）

        Args:
            agent_id: Agent 配置 ID
            message: 任务指令
            thread_id: 线程标识（同一 agent 可多 thread 并行）

        Returns:
            {
                "status": "completed" | "failed",
                "result": dict | None,
                "error_message": str | None,
                "execution_log_id": str,
            }
        """
        agent = self.get_or_create_agent(agent_id)

        log = ElAgentExecutionLog.objects.create(
            agent_id=agent_id,
            thread_id=thread_id,
            status="running",
        )

        events: list[dict[str, Any]] = []
        result_data = None
        error_msg = None

        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": message}]},
                config={"configurable": {"thread_id": thread_id}},
                stream_mode=["updates", "messages"],
            ):
                if isinstance(chunk, dict):
                    events.append(chunk)
                elif hasattr(chunk, "__dict__"):
                    events.append(chunk.__dict__)
                else:
                    events.append({"raw": str(chunk)})

                if isinstance(chunk, dict) and "final_result" in chunk.get("type", ""):
                    result_data = chunk.get("data")

            if result_data is None and events:
                last_event = events[-1]
                if isinstance(last_event, dict):
                    result_data = last_event

            log.status = "completed"
            log.result = result_data
            log.events = events
            log.save()

            logger.info("Agent 执行完成: agent=%s, thread=%s", agent_id, thread_id)

            return {
                "status": "completed",
                "result": result_data,
                "error_message": None,
                "execution_log_id": str(log.id),
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Agent 执行失败: agent=%s, thread=%s, error=%s",
                agent_id, thread_id, error_msg,
            )

            log.status = "failed"
            log.events = events
            log.error_message = error_msg
            log.save()

            return {
                "status": "failed",
                "result": None,
                "error_message": error_msg,
                "execution_log_id": str(log.id),
            }


# 全局单例
orchestrator = Orchestrator()

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

from agent.context import GitContext
from agent.middleware import GitSandboxMiddleware
from agent.models import ElAgent, ElAgentExecutionLog
from agent.services.sandbox_resolver import resolve_backend
from task.middleware.task_memory import TaskMemoryMiddleware

logger = logging.getLogger(__name__)

GIT_SYSTEM_PROMPT_SUFFIX = (
    "\n\n你是一个在沙箱环境中工作的 AI 编程助手。\n"
    "你的工作目录是 /workspace，所有代码修改都在该目录下进行。\n"
    "完成工作后，你必须以 JSON 格式输出以下字段（仅输出 JSON，不要其他内容）：\n"
    '{\n'
    '  "commit_message": "简洁的提交信息，符合 conventional commits 格式",\n'
    '  "pr_title": "Pull Request 标题",\n'
    '  "pr_description": "Pull Request 描述，包括做了什么、如何测试、注意事项",\n'
    '  "summary": "本次工作的简要总结"\n'
    '}'
)


class Orchestrator:
    """Agent 编排器（全局单例）"""

    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._lock = Lock()

    def get_or_create_agent(self, agent_id: str, task_id: str = "") -> Any:
        """获取或创建 Agent 实例（线程安全）"""
        with self._lock:
            cache_key = f"{agent_id}:{task_id}"
            if cache_key not in self._agents:
                self._agents[cache_key] = self._build_agent(agent_id, task_id)
            return self._agents[cache_key]

    def _build_agent(self, agent_id: str, task_id: str = "") -> Any:
        """根据 Agent 配置创建 deep agent 实例"""
        agent_config = ElAgent.objects.get(id=agent_id)

        llm = ChatOpenAI(model=agent_config.model)
        checkpointer = MemorySaver()

        backend = resolve_backend(agent_config)

        # 追加 Git 工作约束到 system_prompt
        system_prompt = agent_config.system_prompt + GIT_SYSTEM_PROMPT_SUFFIX

        # 构建 middleware 列表
        middleware_list = [GitSandboxMiddleware(backend=backend)]
        if task_id:
            middleware_list.insert(0, TaskMemoryMiddleware(task_id=task_id))

        agent = create_deep_agent(
            model=llm,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
            backend=backend,
            context_schema=GitContext,
            middleware=middleware_list,
        )

        logger.info(
            "Agent 实例已创建: %s (id=%s, task_id=%s)",
            agent_config.code,
            agent_id,
            task_id or "none",
        )
        return agent

    def execute(
        self,
        agent_id: str,
        message: str,
        thread_id: str,
        agent_code: str = "",
        task_branch: str = "",
        git_repo_url: str = "",
        git_platform: str = "",
        git_base_path: str = "/workspace",
        git_token_secret: str = "",
        task_id: str = "",
    ) -> dict[str, Any]:
        """
        执行 Agent 任务（同步阻塞）

        Args:
            agent_id: Agent 配置 ID
            message: 任务指令
            thread_id: 线程标识
            agent_code: Agent 编码（用于工作分支命名）
            task_branch: 任务分支名
            git_repo_url: Git 仓库地址（任务级）
            git_platform: Git 平台类型（任务级）
            git_base_path: 沙箱工作目录
            git_token_secret: Token 环境变量 key

        Returns:
            {
                "status": "completed" | "failed",
                "result": dict | None,
                "error_message": str | None,
                "execution_log_id": str,
            }
        """
        agent = self.get_or_create_agent(agent_id, task_id=task_id)

        log = ElAgentExecutionLog.objects.create(
            agent_id=agent_id,
            thread_id=thread_id,
            status="running",
        )

        events: list[dict[str, Any]] = []
        result_data = None
        error_msg = None

        try:
            config: dict[str, Any] = {
                "configurable": {"thread_id": thread_id, "agent_code": agent_code},
            }

            # 传递任务级 Git 配置
            if git_repo_url:
                config["context"] = GitContext(
                    thread_id=thread_id,
                    task_branch=task_branch,
                    git_repo_url=git_repo_url,
                    git_platform=git_platform,
                    git_base_path=git_base_path,
                    git_token_secret=git_token_secret,
                )

            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
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

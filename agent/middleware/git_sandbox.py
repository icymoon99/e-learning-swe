"""Git Sandbox 中间件 — 在 Agent 执行前后自动处理 Git 工作流。

before_agent: clone 仓库 → 创建并切换到工作分支
after_agent:  解析 Agent 输出 → git commit → push → 创建 PR
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urlparse

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from agent.context import GitContext
from agent.services.git_platform import PRRequest, get_platform as _get_platform

logger = logging.getLogger(__name__)


def _build_auth_clone_url(repo_url: str, token: str, platform: str) -> str:
    """将 Token 嵌入 HTTP(S) 仓库 URL 实现认证克隆。

    GitLab: http://oauth2:{token}@host/owner/repo.git
    GitHub: http://{token}@host/owner/repo.git
    Gitee:  http://oauth2:{token}@gitee.com/owner/repo.git
    """
    if not token:
        return repo_url

    parsed = urlparse(repo_url)
    if parsed.scheme not in ("http", "https"):
        return repo_url

    if platform == "github":
        auth_url = f"{parsed.scheme}://{token}@{parsed.netloc}{parsed.path}"
    elif platform == "gitlab":
        auth_url = f"{parsed.scheme}://oauth2:{token}@{parsed.netloc}{parsed.path}"
    elif platform == "gitee":
        auth_url = f"{parsed.scheme}://oauth2:{token}@{parsed.netloc}{parsed.path}"
    else:
        # 未知平台，尝试 GitLab 格式
        auth_url = f"{parsed.scheme}://oauth2:{token}@{parsed.netloc}{parsed.path}"

    return auth_url


class GitSandboxMiddleware(AgentMiddleware):
    """Git 工作流中间件。

    仅在后端实现了 SandboxBackendProtocol（支持 execute）时生效。
    所有 Git 配置通过 context_schema（GitContext）在 invoke 时传入。
    """

    def __init__(self, backend: Any) -> None:
        self.backend = backend
        self._git_context: GitContext | None = None
        self._agent_code: str | None = None

    def before_agent(
        self, state: dict, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Agent 启动前：clone 仓库并创建工作分支。"""
        self._git_context = (
            runtime.context
            if hasattr(runtime, "context") and runtime.context
            else None
        )
        if self._git_context is None:
            logger.debug("GitSandboxMiddleware: 无 GitContext，跳过 before_agent")
            return None

        ctx = self._git_context
        self._agent_code = (
            runtime.config.configurable.get("agent_code", "unknown")
            if hasattr(runtime, "config") and runtime.config
            else "unknown"
        )
        work_branch = (
            f"{ctx.task_branch}_{ctx.thread_id[:8]}_{self._agent_code}"
        )

        try:
            logger.info(
                "GitSandboxMiddleware: 开始 Git 初始化, repo=%s, branch=%s, work_branch=%s",
                ctx.git_repo_url, ctx.task_branch, work_branch,
            )

            if hasattr(self.backend, "ensure_dir"):
                self.backend.ensure_dir()
                logger.info("GitSandboxMiddleware: 沙箱目录已创建")
            elif hasattr(self.backend, "ensure_container"):
                self.backend.ensure_container()
                logger.info("GitSandboxMiddleware: 沙箱容器已就绪")

            clone_url = _build_auth_clone_url(
                ctx.git_repo_url, ctx.git_token, ctx.git_platform
            )

            self._execute_in_sandbox("rm -rf *")
            logger.info("GitSandboxMiddleware: 工作目录已清空")

            self._execute_in_sandbox(f"git clone {clone_url} .")
            logger.info("GitSandboxMiddleware: 代码克隆完成")

            self._execute_in_sandbox(
                'git config user.name "Agent" && '
                'git config user.email "agent@e-learning.local"'
            )
            self._execute_in_sandbox(
                f"git checkout -B {ctx.task_branch} origin/{ctx.task_branch}"
            )
            self._execute_in_sandbox(f"git checkout -b {work_branch}")
            logger.info("GitSandboxMiddleware: 工作分支 %s 已创建", work_branch)

        except Exception as e:
            logger.warning(
                "GitSandboxMiddleware: Git 初始化失败，继续执行 Agent (不影响文件操作): %s", e
            )
            self._git_context = None  # 标记跳过后续 Git 操作

        return None

    def after_agent(
        self, state: dict, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Agent 完成后：提交代码并创建 PR。"""
        if self._git_context is None:
            logger.debug("GitSandboxMiddleware: 无 GitContext，跳过 after_agent")
            return None

        ctx = self._git_context
        work_branch = (
            f"{ctx.task_branch}_{ctx.thread_id[:8]}_{self._agent_code}"
        )

        commit_msg, pr_title, pr_desc = self._parse_agent_output(state)
        logger.info("GitSandboxMiddleware: Agent 输出已解析, commit_msg=%s, pr_title=%s", commit_msg, pr_title)

        try:
            self._execute_in_sandbox("git add -A")
            self._execute_in_sandbox(
                f'git commit -m "{commit_msg}"'
            )
            logger.info("GitSandboxMiddleware: 代码已提交")

            token = ctx.git_token
            if token:
                auth_url = _build_auth_clone_url(
                    ctx.git_repo_url, token, ctx.git_platform
                )
                self._execute_in_sandbox(
                    f"git remote set-url origin {auth_url}"
                )

                self._execute_in_sandbox(
                    f"git push origin {work_branch}"
                )
                logger.info("GitSandboxMiddleware: 分支已推送")

                platform = _get_platform(
                    ctx.git_platform, token, ctx.git_repo_url
                )
                pr_result = platform.create_pr(
                    PRRequest(
                        title=pr_title,
                        description=pr_desc,
                        source_branch=work_branch,
                        target_branch=ctx.task_branch,
                    )
                )

                if pr_result:
                    logger.info(
                        "GitSandboxMiddleware: PR 已创建 %s (#%d)",
                        pr_result["url"],
                        pr_result["number"],
                    )
                    return {
                        "git_pr_url": pr_result["url"],
                        "git_pr_number": pr_result["number"],
                    }
                else:
                    logger.warning("GitSandboxMiddleware: PR 创建失败")
            else:
                logger.info(
                    "GitSandboxMiddleware: 未配置 Git Token，跳过 PR 创建"
                )

        except Exception as e:
            logger.error("GitSandboxMiddleware: Git 提交/PR 失败: %s", e)

        return None

    # ------------------------------------------------------------------ #
    # 内部方法
    # ------------------------------------------------------------------ #

    def _execute_in_sandbox(self, command: str) -> str:
        """在沙箱内执行命令并返回输出。"""
        logger.debug("GitSandboxMiddleware: 执行命令: %s", command)
        result = self.backend.execute(command)
        if result.exit_code != 0:
            raise RuntimeError(
                f"沙箱执行失败: {command}\n输出: {result.output}"
            )
        return result.output

    def _parse_agent_output(
        self, state: dict
    ) -> tuple[str, str, str]:
        """从 Agent 最终 state 中解析 JSON 输出。

        期望格式：
        {
            "commit_message": "...",
            "pr_title": "...",
            "pr_description": "...",
            "summary": "..."
        }

        如果解析失败，返回默认值。
        """
        default_commit = "feat: agent 完成工作"
        default_title = "Agent 完成工作"
        default_desc = "由 Agent 自动生成"

        try:
            messages = state.get("messages", [])
            if not messages:
                return default_commit, default_title, default_desc

            # 找最后一条 AI 消息（跳过 tool 消息）
            last_ai_msg = None
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    last_ai_msg = msg
                    break

            if last_ai_msg is None:
                return default_commit, default_title, default_desc

            content = last_ai_msg.content

            # 提取 JSON 块（可能包裹在 ```json ... ``` 中）
            if "```" in content:
                for block in content.split("```"):
                    block = block.strip()
                    if block.startswith("json"):
                        block = block[4:].strip()
                    if block.startswith("{"):
                        data = json.loads(block)
                        return (
                            data.get("commit_message", default_commit),
                            data.get("pr_title", default_title),
                            data.get("pr_description", default_desc),
                        )

            # 尝试直接解析整个 content
            if content.strip().startswith("{"):
                data = json.loads(content)
                return (
                    data.get("commit_message", default_commit),
                    data.get("pr_title", default_title),
                    data.get("pr_description", default_desc),
                )

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(
                "GitSandboxMiddleware: 无法解析 Agent JSON 输出: %s", e
            )

        return default_commit, default_title, default_desc

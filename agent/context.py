from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GitContext:
    """任务级 Git 配置，通过 context_schema 传递给 middleware。

    每次 invoke Agent 时由 Orchestrator 构造并传入。
    """

    thread_id: str         # 每次 invoke 的执行标识
    task_branch: str       # 任务分支名
    git_repo_url: str      # Git 仓库地址
    git_platform: str      # 平台类型：github / gitee / gitlab
    git_token: str = ""                     # Token 实际值（从 ElGitSource.token 获取）

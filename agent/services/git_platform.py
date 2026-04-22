"""Git 平台抽象层 — 统一 PR 创建接口，支持 GitHub / Gitee / GitLab。"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


@dataclass
class PRRequest:
    """PR 创建请求"""

    title: str
    description: str
    source_branch: str
    target_branch: str


def parse_repo_owner_and_name(repo_url: str, platform: str) -> tuple[str, str]:
    """从仓库 URL 中解析 owner 和 repo name。

    GitHub: https://github.com/owner/repo.git → (owner, repo)
    GitHub: git@github.com:owner/repo.git → (owner, repo)
    Gitee:  https://gitee.com/owner/repo.git → (owner, repo)
    GitLab: https://gitlab.com/group/subgroup/repo.git → (group/subgroup, repo)
    """
    ssh_match = re.match(r"git@[^:]+:(.+)/(.+?)\.git$", repo_url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    parsed = urlparse(repo_url)
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.rsplit("/", 1)
    if len(parts) != 2:
        raise ValueError(f"无法从 URL 解析 owner/repo: {repo_url}")
    return parts[0], parts[1]


class GitPlatform(ABC):
    """Git 平台抽象基类"""

    @abstractmethod
    def create_pr(self, req: PRRequest) -> dict | None:
        """创建 PR/MR。

        Returns:
            {"url": str, "number": int} 或 None（创建失败时）
        """
        ...


class GitHubPlatform(GitPlatform):
    """GitHub PR 创建"""

    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.token = token
        self._owner = owner
        self._repo = repo

    def create_pr(self, req: PRRequest) -> dict | None:
        url = f"https://api.github.com/repos/{self._owner}/{self._repo}/pulls"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "title": req.title,
            "body": req.description,
            "head": req.source_branch,
            "base": req.target_branch,
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException:
            logger.exception("GitHub PR 创建异常")
            return None

        if resp.status_code == 201:
            result = resp.json()
            return {"url": result["html_url"], "number": result["number"]}
        logger.error("GitHub PR 创建失败: %s %s", resp.status_code, resp.text)
        return None


class GiteePlatform(GitPlatform):
    """Gitee PR 创建"""

    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.token = token
        self._owner = owner
        self._repo = repo

    def create_pr(self, req: PRRequest) -> dict | None:
        url = f"https://gitee.com/api/v5/repos/{self._owner}/{self._repo}/pulls"
        data = {
            "access_token": self.token,
            "title": req.title,
            "body": req.description,
            "head": req.source_branch,
            "base": req.target_branch,
        }

        try:
            resp = requests.post(url, data=data, timeout=30)
        except requests.exceptions.RequestException:
            logger.exception("Gitee PR 创建异常")
            return None

        if resp.status_code == 201:
            result = resp.json()
            return {"url": result["html_url"], "number": result["number"]}
        logger.error("Gitee PR 创建失败: %s %s", resp.status_code, resp.text)
        return None


class GitLabPlatform(GitPlatform):
    """GitLab MR 创建"""

    def __init__(self, token: str, project_id: str) -> None:
        self.token = token
        self.project_id = project_id

    def create_pr(self, req: PRRequest) -> dict | None:
        url = f"https://gitlab.com/api/v4/projects/{self.project_id}/merge_requests"
        headers = {"PRIVATE-TOKEN": self.token}
        data = {
            "title": req.title,
            "description": req.description,
            "source_branch": req.source_branch,
            "target_branch": req.target_branch,
        }

        try:
            resp = requests.post(url, headers=headers, data=data, timeout=30)
        except requests.exceptions.RequestException:
            logger.exception("GitLab MR 创建异常")
            return None

        if resp.status_code == 201:
            result = resp.json()
            return {"url": result["web_url"], "number": result["iid"]}
        logger.error("GitLab MR 创建失败: %s %s", resp.status_code, resp.text)
        return None


def get_platform(platform: str, token: str, repo_url: str) -> GitPlatform:
    """工厂函数 — 根据平台类型返回对应 GitPlatform 实例。"""
    owner, repo = parse_repo_owner_and_name(repo_url, platform)

    if platform == "github":
        return GitHubPlatform(token=token, owner=owner, repo=repo)
    elif platform == "gitee":
        return GiteePlatform(token=token, owner=owner, repo=repo)
    elif platform == "gitlab":
        project_id = owner.replace("/", "%2F") + "%2F" + repo
        return GitLabPlatform(token=token, project_id=project_id)
    else:
        raise ValueError(f"Unsupported platform: {platform}")


def get_platform_from_source(source_id: str) -> "GitPlatform":
    """根据仓库源 ID 获取对应的 GitPlatform 实例。

    Args:
        source_id: ElGitSource 的 ULID 主键

    Returns:
        对应的 GitPlatform 实例
    """
    from git_source.models import ElGitSource

    source = ElGitSource.objects.get(id=source_id)
    return get_platform(source.platform, source.token, source.repo_url)

from typing import Any

import requests

# 平台默认 API 地址（作为后端常量）
PLATFORM_API_URLS = {
    "github": "https://api.github.com",
    "gitee": "https://gitee.com/api/v5",
    # GitLab 不使用默认值，由 api_url 参数指定
}


def list_remote_repos(
    platform: str, token: str, api_url: str | None = None
) -> list[dict[str, Any]]:
    """根据平台和 Token 获取用户有权限的所有仓库列表"""
    if platform == "github":
        return _list_github_repos(token)
    elif platform == "gitee":
        return _list_gitee_repos(token)
    elif platform == "gitlab":
        return _list_gitlab_repos(token, api_url=api_url)
    else:
        raise ValueError(f"不支持的平台: {platform}")


def _list_github_repos(token: str) -> list[dict[str, Any]]:
    """获取 GitHub 仓库列表（用户有权限的所有仓库）"""
    headers = {"Authorization": f"token {token}"}
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        resp = requests.get(
            f"{PLATFORM_API_URLS['github']}/user/repos",
            headers=headers,
            params={
                "per_page": 100,
                "page": page,
                "affiliation": "owner,collaborator,organization_member",
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        for item in items:
            repos.append({
                "name": item["name"],
                "full_name": item["full_name"],
                "url": item["clone_url"],
                "default_branch": item.get("default_branch", "main"),
                "description": item.get("description", ""),
            })
        page += 1
    return repos


def _list_gitee_repos(token: str) -> list[dict[str, Any]]:
    """获取 Gitee 仓库列表"""
    headers = {"Authorization": f"token {token}"}
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        resp = requests.get(
            f"{PLATFORM_API_URLS['gitee']}/user/repos",
            headers=headers,
            params={
                "per_page": 100,
                "page": page,
                "affiliation": "owner,collaborator",
            },
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        for item in items:
            namespace = item.get("namespace", {})
            namespace_path = namespace.get("path", "") if namespace else ""
            repos.append({
                "name": item["name"],
                "full_name": f"{namespace_path}/{item['name']}",
                "url": item.get("https_url_to_repo") or f"{item['html_url']}.git",
                "default_branch": item.get("default_branch", "master"),
                "description": item.get("description", ""),
            })
        page += 1
    return repos


def _list_gitlab_repos(
    token: str, api_url: str | None = None
) -> list[dict[str, Any]]:
    """获取 GitLab 仓库列表（支持私有部署）"""
    base_url = (api_url or "https://gitlab.com").rstrip("/") + "/api/v4"
    headers = {"PRIVATE-TOKEN": token}
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        resp = requests.get(
            f"{base_url}/projects",
            headers=headers,
            params={"per_page": 100, "page": page, "membership": "true"},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        for item in items:
            repos.append({
                "name": item["name"],
                "full_name": item["path_with_namespace"],
                "url": item["http_url_to_repo"],
                "default_branch": item.get("default_branch", "main"),
                "description": item.get("description", ""),
            })
        page += 1
    return repos


def list_branches(
    platform: str,
    token: str,
    repo_full_name: str,
    api_url: str | None = None,
) -> dict[str, Any]:
    """获取指定仓库的所有分支列表，返回 {default_branch, branches}"""
    if platform == "github":
        return _list_github_branches(token, repo_full_name)
    elif platform == "gitee":
        return _list_gitee_branches(token, repo_full_name)
    elif platform == "gitlab":
        return _list_gitlab_branches(token, repo_full_name, api_url=api_url)
    else:
        raise ValueError(f"不支持的平台: {platform}")


def _list_github_branches(
    token: str, repo_full_name: str
) -> dict[str, Any]:
    """获取 GitHub 仓库分支列表"""
    headers = {"Authorization": f"token {token}"}
    branches: list[str] = []
    page = 1
    default_branch: str | None = None
    while True:
        resp = requests.get(
            f"{PLATFORM_API_URLS['github']}/repos/{repo_full_name}/branches",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        branches.extend([item["name"] for item in items])
        page += 1
    repo_resp = requests.get(
        f"{PLATFORM_API_URLS['github']}/repos/{repo_full_name}",
        headers=headers,
        timeout=15,
    )
    if repo_resp.status_code == 200:
        default_branch = repo_resp.json().get("default_branch", "main")
    return {"default_branch": default_branch or "main", "branches": branches}


def _list_gitee_branches(
    token: str, repo_full_name: str
) -> dict[str, Any]:
    """获取 Gitee 仓库分支列表"""
    headers = {"Authorization": f"token {token}"}
    owner, repo = repo_full_name.split("/", 1)
    branches: list[str] = []
    page = 1
    default_branch: str | None = None
    while True:
        resp = requests.get(
            f"{PLATFORM_API_URLS['gitee']}/repos/{owner}/{repo}/branches",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        branches.extend([item["name"] for item in items])
        page += 1
    repo_resp = requests.get(
        f"{PLATFORM_API_URLS['gitee']}/repos/{owner}/{repo}",
        headers=headers,
        timeout=15,
    )
    if repo_resp.status_code == 200:
        default_branch = repo_resp.json().get("default_branch", "master")
    return {"default_branch": default_branch or "master", "branches": branches}


def _list_gitlab_branches(
    token: str, repo_full_name: str, api_url: str | None = None
) -> dict[str, Any]:
    """获取 GitLab 仓库分支列表"""
    import urllib.parse

    base_url = (api_url or "https://gitlab.com").rstrip("/") + "/api/v4"
    headers = {"PRIVATE-TOKEN": token}
    encoded_path = urllib.parse.quote(repo_full_name, safe="")
    proj_resp = requests.get(
        f"{base_url}/projects/{encoded_path}",
        headers=headers,
        timeout=15,
    )
    proj_resp.raise_for_status()
    proj_data = proj_resp.json()
    project_id = proj_data["id"]
    default_branch = proj_data.get("default_branch", "main")
    branches: list[str] = []
    page = 1
    while True:
        resp = requests.get(
            f"{base_url}/projects/{project_id}/repository/branches",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        branches.extend([item["name"] for item in items])
        page += 1
    return {"default_branch": default_branch, "branches": branches}

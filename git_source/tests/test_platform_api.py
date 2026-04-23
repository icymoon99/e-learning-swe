from unittest.mock import patch, MagicMock
from django.test import TestCase

from git_source.services.platform_api import (
    list_remote_repos,
    list_branches,
    PLATFORM_API_URLS,
)


def _make_resp(json_data):
    """Helper to create a mock response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


class ListRemoteReposTest(TestCase):
    """list_remote_repos 函数测试"""

    def test_unsupported_platform(self):
        """不支持的平台抛出 ValueError"""
        with self.assertRaises(ValueError) as ctx:
            list_remote_repos("bitbucket", "token")
        self.assertIn("不支持的平台", str(ctx.exception))

    @patch("git_source.services.platform_api.requests.get")
    def test_github_repos_single_page(self, mock_get):
        """GitHub 单页仓库列表"""
        items = [{
            "name": "repo1",
            "full_name": "org/repo1",
            "clone_url": "https://github.com/org/repo1.git",
            "default_branch": "main",
            "description": "test repo",
        }]
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            return _make_resp(items if call_count[0] == 1 else [])

        mock_get.side_effect = side_effect

        repos = list_remote_repos("github", "ghp_token")

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "repo1")
        self.assertEqual(repos[0]["full_name"], "org/repo1")
        self.assertEqual(repos[0]["default_branch"], "main")

    @patch("git_source.services.platform_api.requests.get")
    def test_github_repos_pagination(self, mock_get):
        """GitHub 多页仓库列表"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if page == 1:
                return _make_resp([
                    {"name": f"repo{i}", "full_name": f"org/repo{i}",
                     "clone_url": f"https://github.com/org/repo{i}.git",
                     "default_branch": "main", "description": ""}
                    for i in range(1, 101)
                ])
            elif page == 2:
                return _make_resp([
                    {"name": "repo101", "full_name": "org/repo101",
                     "clone_url": "https://github.com/org/repo101.git",
                     "default_branch": "main", "description": ""}
                ])
            return _make_resp([])

        mock_get.side_effect = side_effect

        repos = list_remote_repos("github", "ghp_token")
        self.assertEqual(len(repos), 101)

    @patch("git_source.services.platform_api.requests.get")
    def test_gitee_repos(self, mock_get):
        """Gitee 仓库列表"""
        items = [{
            "name": "myrepo",
            "namespace": {"path": "my-org"},
            "https_url_to_repo": "https://gitee.com/my-org/myrepo.git",
            "default_branch": "master",
            "description": "gitee repo",
        }]
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            return _make_resp(items if call_count[0] == 1 else [])

        mock_get.side_effect = side_effect

        repos = list_remote_repos("gitee", "gitee_token")

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["full_name"], "my-org/myrepo")
        self.assertEqual(repos[0]["default_branch"], "master")

    @patch("git_source.services.platform_api.requests.get")
    def test_gitee_repos_fallback_url(self, mock_get):
        """Gitee https_url_to_repo 为空时使用 html_url 拼接"""
        items = [{
            "name": "myrepo",
            "namespace": {"path": "my-org"},
            "https_url_to_repo": "",
            "html_url": "https://gitee.com/my-org/myrepo",
            "default_branch": "master",
            "description": "",
        }]
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            return _make_resp(items if call_count[0] == 1 else [])

        mock_get.side_effect = side_effect

        repos = list_remote_repos("gitee", "gitee_token")
        self.assertEqual(repos[0]["url"], "https://gitee.com/my-org/myrepo.git")

    @patch("git_source.services.platform_api.requests.get")
    def test_gitlab_repos(self, mock_get):
        """GitLab 仓库列表"""
        items = [{
            "name": "project1",
            "path_with_namespace": "my-group/project1",
            "http_url_to_repo": "https://gitlab.com/my-group/project1.git",
            "default_branch": "main",
            "description": "gitlab project",
        }]
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            return _make_resp(items if call_count[0] == 1 else [])

        mock_get.side_effect = side_effect

        repos = list_remote_repos("gitlab", "gl_token")

        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["full_name"], "my-group/project1")

    @patch("git_source.services.platform_api.requests.get")
    def test_gitlab_repos_custom_api_url(self, mock_get):
        """GitLab 自定义 API 地址"""
        mock_get.return_value = _make_resp([])

        list_remote_repos("gitlab", "gl_token", api_url="https://git.example.com")

        call_args = mock_get.call_args
        self.assertIn("git.example.com", call_args.args[0])


class ListBranchesTest(TestCase):
    """list_branches 函数测试"""

    def test_unsupported_platform(self):
        """不支持的平台抛出 ValueError"""
        with self.assertRaises(ValueError) as ctx:
            list_branches("bitbucket", "token", "org/repo")
        self.assertIn("不支持的平台", str(ctx.exception))

    @patch("git_source.services.platform_api.requests.get")
    def test_github_branches(self, mock_get):
        """GitHub 分支列表"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if "/branches" in url:
                if page == 1:
                    return _make_resp([{"name": "main"}, {"name": "develop"}])
                return _make_resp([])
            return _make_resp({"default_branch": "main"})

        mock_get.side_effect = side_effect

        result = list_branches("github", "ghp_token", "org/repo")

        self.assertEqual(result["default_branch"], "main")
        self.assertEqual(result["branches"], ["main", "develop"])

    @patch("git_source.services.platform_api.requests.get")
    def test_gitee_branches(self, mock_get):
        """Gitee 分支列表"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if "/branches" in url:
                if page == 1:
                    return _make_resp([{"name": "master"}, {"name": "dev"}])
                return _make_resp([])
            return _make_resp({"default_branch": "master"})

        mock_get.side_effect = side_effect

        result = list_branches("gitee", "gitee_token", "my-org/myrepo")

        self.assertEqual(result["default_branch"], "master")
        self.assertEqual(len(result["branches"]), 2)

    @patch("git_source.services.platform_api.requests.get")
    def test_gitlab_branches(self, mock_get):
        """GitLab 分支列表"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if "/projects/" in url and "/repository/branches" not in url:
                return _make_resp({"id": 12345, "default_branch": "main"})
            elif "/repository/branches" in url:
                if page == 1:
                    return _make_resp([{"name": "main"}, {"name": "feature/x"}])
                return _make_resp([])
            return _make_resp([])

        mock_get.side_effect = side_effect

        result = list_branches("gitlab", "gl_token", "my-group/project1")

        self.assertEqual(result["default_branch"], "main")
        self.assertEqual(len(result["branches"]), 2)

    @patch("git_source.services.platform_api.requests.get")
    def test_gitlab_branches_custom_api_url(self, mock_get):
        """GitLab 分支查询使用自定义 API 地址"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if "/projects/" in url and "/repository/branches" not in url:
                return _make_resp({"id": 1, "default_branch": "main"})
            elif "/repository/branches" in url:
                if page == 1:
                    return _make_resp([{"name": "main"}])
                return _make_resp([])
            return _make_resp([])

        mock_get.side_effect = side_effect

        result = list_branches(
            "gitlab", "gl_token", "my-group/project1",
            api_url="https://git.example.com"
        )

        call_args = mock_get.call_args_list[0]
        self.assertIn("git.example.com", call_args.args[0])
        self.assertEqual(result["default_branch"], "main")


class PlatformApiConstantsTest(TestCase):
    """平台 API 常量测试"""

    def test_platform_urls_contains_github(self):
        """PLATFORM_API_URLS 包含 GitHub"""
        self.assertIn("github", PLATFORM_API_URLS)
        self.assertEqual(PLATFORM_API_URLS["github"], "https://api.github.com")

    def test_platform_urls_contains_gitee(self):
        """PLATFORM_API_URLS 包含 Gitee"""
        self.assertIn("gitee", PLATFORM_API_URLS)
        self.assertEqual(PLATFORM_API_URLS["gitee"], "https://gitee.com/api/v5")

    def test_gitlab_not_in_default_urls(self):
        """GitLab 不使用默认 API 地址"""
        self.assertNotIn("gitlab", PLATFORM_API_URLS)

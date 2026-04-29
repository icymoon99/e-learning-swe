from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agent.services.git_platform import (
    PRRequest,
    GitHubPlatform,
    GiteePlatform,
    GitLabPlatform,
    get_platform,
    parse_repo_owner_and_name,
)


class TestParseRepoOwnerAndName:
    """parse_repo_owner_and_name 函数测试"""

    def test_github_https_url(self):
        owner, name = parse_repo_owner_and_name(
            "https://github.com/owner/repo.git", "github"
        )
        assert owner == "owner"
        assert name == "repo"

    def test_github_https_url_no_git_suffix(self):
        owner, name = parse_repo_owner_and_name(
            "https://github.com/owner/repo", "github"
        )
        assert owner == "owner"
        assert name == "repo"

    def test_github_ssh_url(self):
        owner, name = parse_repo_owner_and_name(
            "git@github.com:owner/repo.git", "github"
        )
        assert owner == "owner"
        assert name == "repo"

    def test_gitee_https_url(self):
        owner, name = parse_repo_owner_and_name(
            "https://gitee.com/owner/repo.git", "gitee"
        )
        assert owner == "owner"
        assert name == "repo"

    def test_gitlab_nested_group(self):
        owner, name = parse_repo_owner_and_name(
            "https://gitlab.com/group/subgroup/repo.git", "gitlab"
        )
        assert owner == "group/subgroup"
        assert name == "repo"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="无法从 URL 解析"):
            parse_repo_owner_and_name("https://example.com/repo.git", "github")


class TestGitHubPlatform:
    """GitHub PR 创建测试"""

    @patch("agent.services.git_platform.requests.post")
    def test_create_pr_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "html_url": "https://github.com/owner/repo/pull/42",
            "number": 42,
        }
        mock_post.return_value = mock_resp

        platform = GitHubPlatform(token="gh_token", owner="owner", repo="repo")
        result = platform.create_pr(PRRequest(
            title="Add feature",
            description="Description here",
            source_branch="feature/work",
            target_branch="main",
        ))

        assert result is not None
        assert result["url"] == "https://github.com/owner/repo/pull/42"
        assert result["number"] == 42
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "token gh_token"
        assert call_kwargs["json"]["head"] == "feature/work"
        assert call_kwargs["json"]["base"] == "main"

    @patch("agent.services.git_platform.requests.post")
    def test_create_pr_422_returns_none(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 422
        mock_resp.text = "Unprocessable Entity"
        mock_post.return_value = mock_resp

        platform = GitHubPlatform(token="gh_token", owner="owner", repo="repo")
        result = platform.create_pr(PRRequest(
            title="Add feature",
            description="Description",
            source_branch="feature/work",
            target_branch="main",
        ))

        assert result is None

    @patch("agent.services.git_platform.requests.post")
    def test_create_pr_timeout_returns_none(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        platform = GitHubPlatform(token="gh_token", owner="owner", repo="repo")
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="main",
        ))

        assert result is None


class TestGiteePlatform:
    """Gitee PR 创建测试"""

    @patch("agent.services.git_platform.requests.post")
    def test_create_pr_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "html_url": "https://gitee.com/owner/repo/pulls/10",
            "number": 10,
        }
        mock_post.return_value = mock_resp

        platform = GiteePlatform(token="gitee_token", owner="owner", repo="repo")
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="main",
        ))

        assert result is not None
        assert result["url"] == "https://gitee.com/owner/repo/pulls/10"
        assert result["number"] == 10
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["data"]["access_token"] == "gitee_token"

    @patch("agent.services.git_platform.requests.post")
    def test_create_pr_failure(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_post.return_value = mock_resp

        platform = GiteePlatform(token="gitee_token", owner="owner", repo="repo")
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="main",
        ))

        assert result is None


class TestGitLabPlatform:
    """GitLab MR 创建测试"""

    @patch("agent.services.git_platform.requests.post")
    def test_create_mr_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "web_url": "https://gitlab.com/group/repo/-/merge_requests/5",
            "iid": 5,
        }
        mock_post.return_value = mock_resp

        platform = GitLabPlatform(token="gl_token", project_id="123")
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="main",
        ))

        assert result is not None
        assert result["url"] == "https://gitlab.com/group/repo/-/merge_requests/5"
        assert result["number"] == 5
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["PRIVATE-TOKEN"] == "gl_token"
        # 默认 API base 应为 gitlab.com
        call_args = mock_post.call_args
        assert "https://gitlab.com/api/v4/projects/123/merge_requests" in call_args[0][0]

    @patch("agent.services.git_platform.requests.post")
    def test_create_mr_self_hosted(self, mock_post):
        """自托管 GitLab 应使用正确的 API base URL"""
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "web_url": "http://192.168.1.38/group/repo/-/merge_requests/1",
            "iid": 1,
        }
        mock_post.return_value = mock_resp

        platform = GitLabPlatform(
            token="gl_token",
            project_id="oio-smart%2Foio_smart_resource_mcp",
            api_base="http://192.168.1.38",
        )
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="dev",
        ))

        assert result is not None
        call_args = mock_post.call_args
        assert "http://192.168.1.38/api/v4/projects/" in call_args[0][0]

    @patch("agent.services.git_platform.requests.post")
    def test_create_mr_failure(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_post.return_value = mock_resp

        platform = GitLabPlatform(token="gl_token", project_id="123")
        result = platform.create_pr(PRRequest(
            title="Test",
            description="Desc",
            source_branch="work",
            target_branch="main",
        ))

        assert result is None


class TestGetPlatform:
    """get_platform 工厂函数测试"""

    def test_returns_github(self):
        p = get_platform("github", "tok", "https://github.com/o/r.git")
        assert isinstance(p, GitHubPlatform)

    def test_returns_gitee(self):
        p = get_platform("gitee", "tok", "https://gitee.com/o/r.git")
        assert isinstance(p, GiteePlatform)

    def test_returns_gitlab(self):
        p = get_platform("gitlab", "tok", "https://gitlab.com/o/r.git")
        assert isinstance(p, GitLabPlatform)
        assert p.api_base == "https://gitlab.com"

    def test_returns_gitlab_self_hosted(self):
        """自托管 GitLab 应使用正确的 API base"""
        p = get_platform("gitlab", "tok", "http://192.168.1.38/oio-smart/repo.git")
        assert isinstance(p, GitLabPlatform)
        assert p.api_base == "http://192.168.1.38"
        assert p.project_id == "oio-smart%2Frepo"

    def test_unknown_platform_raises(self):
        with pytest.raises(ValueError, match="Unsupported platform"):
            get_platform("bitbucket", "tok", "https://bitbucket.org/o/r.git")

    def test_github_has_correct_owner_repo(self):
        p = get_platform("github", "tok", "https://github.com/myorg/myrepo.git")
        assert isinstance(p, GitHubPlatform)
        assert p._owner == "myorg"
        assert p._repo == "myrepo"

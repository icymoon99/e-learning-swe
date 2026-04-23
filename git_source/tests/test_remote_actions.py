from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class RemoteReposActionTest(TestCase):
    """GET /api/git-source/sources/repos/ action 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_superuser=False
        )

    def test_missing_platform(self):
        """缺少 platform 参数返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/repos/", {"token": "xxx"})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    def test_missing_token(self):
        """缺少 token 参数返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/repos/", {"platform": "github"})
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    @patch("git_source.services.platform_api.requests.get")
    def test_success_returns_repos(self, mock_get):
        """成功获取仓库列表"""
        call_count = [0]

        def side_effect(url, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return _make_resp([
                    {"name": "repo1", "full_name": "org/repo1",
                     "clone_url": "https://github.com/org/repo1.git",
                     "default_branch": "main", "description": ""}
                ])
            return _make_resp([])

        mock_get.side_effect = side_effect

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/repos/", {
            "platform": "github",
            "token": "ghp_xxx",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(len(data["content"]["repos"]), 1)
        self.assertEqual(data["content"]["repos"][0]["name"], "repo1")

    @patch("git_source.services.platform_api.requests.get")
    def test_gitlab_with_api_url(self, mock_get):
        """GitLab 支持自定义 api_url"""
        mock_get.return_value = _make_resp([])

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/repos/", {
            "platform": "gitlab",
            "token": "gl_token",
            "api_url": "https://git.example.com",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)

    @patch("git_source.services.platform_api.list_remote_repos")
    def test_service_exception_returns_error(self, mock_list):
        """服务层异常返回错误信息"""
        mock_list.side_effect = Exception("网络超时")

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/repos/", {
            "platform": "github",
            "token": "ghp_xxx",
        })
        data = resp.json()
        self.assertNotEqual(data["code"], 0)
        self.assertIn("获取仓库列表失败", data["message"])


class RemoteBranchesActionTest(TestCase):
    """GET /api/git-source/sources/branches/ action 测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_superuser=False
        )

    def test_missing_platform(self):
        """缺少 platform 参数返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/branches/", {
            "token": "xxx",
            "repo_full_name": "org/repo",
        })
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    def test_missing_token(self):
        """缺少 token 参数返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/branches/", {
            "platform": "github",
            "repo_full_name": "org/repo",
        })
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    def test_missing_repo_full_name(self):
        """缺少 repo_full_name 参数返回错误"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/branches/", {
            "platform": "github",
            "token": "xxx",
        })
        data = resp.json()
        self.assertNotEqual(data["code"], 0)

    @patch("git_source.services.platform_api.requests.get")
    def test_success_returns_branches(self, mock_get):
        """成功获取分支列表"""
        def side_effect(url, *args, **kwargs):
            page = kwargs.get("params", {}).get("page", 1)
            if "/branches" in url:
                if page == 1:
                    return _make_resp([{"name": "main"}, {"name": "develop"}])
                return _make_resp([])
            return _make_resp({"default_branch": "main"})

        mock_get.side_effect = side_effect

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/branches/", {
            "platform": "github",
            "token": "ghp_xxx",
            "repo_full_name": "org/repo",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("default_branch", data["content"])
        self.assertIn("branches", data["content"])

    @patch("git_source.services.platform_api.list_branches")
    def test_service_exception_returns_error(self, mock_list):
        """服务层异常返回错误信息"""
        mock_list.side_effect = Exception("仓库不存在")

        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/branches/", {
            "platform": "github",
            "token": "ghp_xxx",
            "repo_full_name": "org/repo",
        })
        data = resp.json()
        self.assertNotEqual(data["code"], 0)
        self.assertIn("获取分支列表失败", data["message"])


def _make_resp(json_data):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp

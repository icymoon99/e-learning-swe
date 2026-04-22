from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from git_source.models import ElGitSource

User = get_user_model()


class GitSourceApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", is_superuser=False
        )
        self.admin = User.objects.create_user(
            username="admin", password="adminpass123", is_superuser=True
        )
        ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
            default_branch="main",
        )

    def test_list_requires_auth(self):
        """未认证无法列表"""
        resp = self.client.get("/api/git-source/sources/")
        self.assertEqual(resp.status_code, 401)

    def test_list_returns_sources(self):
        """认证用户可获取列表"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["content"]["count"], 1)

    def test_list_does_not_expose_token(self):
        """列表不返回 token"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/")
        data = resp.json()
        result = data["content"]["results"][0]
        self.assertNotIn("token", result)

    def test_retrieve_does_not_expose_token(self):
        """详情不返回 token"""
        self.client.force_authenticate(user=self.user)
        source = ElGitSource.objects.first()
        resp = self.client.get(f"/api/git-source/sources/{source.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("token", resp.json()["content"])

    def test_create_requires_admin(self):
        """非管理员无法创建"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/git-source/sources/", data={
            "name": "new-gitee",
            "platform": "gitee",
            "repo_url": "https://gitee.com/a/b.git",
            "token": "gitee_token",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_by_admin(self):
        """管理员可创建"""
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/git-source/sources/", data={
            "name": "new-gitee",
            "platform": "gitee",
            "repo_url": "https://gitee.com/a/b.git",
            "token": "gitee_token",
            "default_branch": "master",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(ElGitSource.objects.count(), 2)

    def test_update_requires_admin(self):
        """非管理员无法更新"""
        self.client.force_authenticate(user=self.user)
        source = ElGitSource.objects.first()
        resp = self.client.patch(f"/api/git-source/sources/{source.id}/", data={
            "name": "updated-name",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_update_by_admin(self):
        """管理员可更新"""
        self.client.force_authenticate(user=self.admin)
        source = ElGitSource.objects.first()
        resp = self.client.patch(f"/api/git-source/sources/{source.id}/", data={
            "name": "updated-name",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        source.refresh_from_db()
        self.assertEqual(source.name, "updated-name")

    def test_delete_requires_admin(self):
        """非管理员无法删除"""
        self.client.force_authenticate(user=self.user)
        source = ElGitSource.objects.first()
        resp = self.client.delete(f"/api/git-source/sources/{source.id}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_by_admin(self):
        """管理员可删除"""
        self.client.force_authenticate(user=self.admin)
        source = ElGitSource.objects.first()
        sid = source.id
        resp = self.client.delete(f"/api/git-source/sources/{sid}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ElGitSource.objects.filter(id=sid).exists())

    def test_dropdown_endpoint(self):
        """下拉接口返回精简字段且不包含 token"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/dropdown/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        result = data["content"][0]
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertNotIn("token", result)

    def test_filter_by_platform(self):
        """支持按平台类型过滤"""
        ElGitSource.objects.create(
            name="test-gitee",
            platform="gitee",
            repo_url="https://gitee.com/a/b.git",
            token="tok",
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/?platform=github")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_search_by_name(self):
        """支持按名称搜索"""
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/git-source/sources/?search=test-github")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

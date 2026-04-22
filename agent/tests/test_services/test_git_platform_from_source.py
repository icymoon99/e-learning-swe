from django.test import TestCase
from git_source.models import ElGitSource
from agent.services.git_platform import get_platform_from_source


class GetPlatformFromSourceTest(TestCase):
    def setUp(self):
        self.github_source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_token123",
        )
        self.gitee_source = ElGitSource.objects.create(
            name="test-gitee",
            platform="gitee",
            repo_url="https://gitee.com/owner/repo.git",
            token="gitee_token123",
        )

    def test_github_platform(self):
        """GitHub 源返回 GitHubPlatform"""
        platform = get_platform_from_source(self.github_source.id)
        self.assertEqual(platform.__class__.__name__, "GitHubPlatform")

    def test_gitee_platform(self):
        """Gitee 源返回 GiteePlatform"""
        platform = get_platform_from_source(self.gitee_source.id)
        self.assertEqual(platform.__class__.__name__, "GiteePlatform")

    def test_nonexistent_source_raises_error(self):
        """不存在的源 ID 抛出 DoesNotExist"""
        with self.assertRaises(ElGitSource.DoesNotExist):
            get_platform_from_source("01KPG000000000000000000099")

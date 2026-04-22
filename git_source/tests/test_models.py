from django.test import TestCase
from django.db import IntegrityError
from git_source.models import ElGitSource


class ElGitSourceModelTest(TestCase):
    """ElGitSource 模型基础测试"""

    def test_create_git_source(self):
        """正常创建仓库源"""
        source = ElGitSource.objects.create(
            name="test-github",
            platform="github",
            repo_url="https://github.com/owner/repo.git",
            token="ghp_xxx",
            default_branch="main",
        )
        self.assertEqual(source.name, "test-github")
        self.assertEqual(source.platform, "github")
        self.assertIsNotNone(source.id)
        self.assertEqual(source.default_branch, "main")

    def test_name_must_be_unique(self):
        """名称唯一性约束"""
        ElGitSource.objects.create(
            name="duplicate",
            platform="github",
            repo_url="https://github.com/a/b.git",
            token="tok",
        )
        with self.assertRaises(IntegrityError):
            ElGitSource.objects.create(
                name="duplicate",
                platform="gitee",
                repo_url="https://gitee.com/c/d.git",
                token="tok2",
            )

    def test_platform_choices_display(self):
        """平台选择显示文本"""
        source = ElGitSource.objects.create(
            name="test-gitlab",
            platform="gitlab",
            repo_url="https://gitlab.com/e/f.git",
            token="glp_xxx",
        )
        self.assertEqual(source.get_platform_display(), "GitLab")

    def test_default_branch_default_value(self):
        """默认分支默认值为 main"""
        source = ElGitSource.objects.create(
            name="test-default",
            platform="github",
            repo_url="https://github.com/a/b.git",
            token="tok",
        )
        self.assertEqual(source.default_branch, "main")

    def test_description_can_be_empty(self):
        """备注可以为空"""
        source = ElGitSource.objects.create(
            name="test-empty-desc",
            platform="github",
            repo_url="https://github.com/a/b.git",
            token="tok",
            description="",
        )
        self.assertEqual(source.description, "")

    def test_str_representation(self):
        """字符串表示"""
        source = ElGitSource.objects.create(
            name="my-source",
            platform="gitee",
            repo_url="https://gitee.com/a/b.git",
            token="tok",
        )
        self.assertEqual(str(source), "my-source (Gitee)")

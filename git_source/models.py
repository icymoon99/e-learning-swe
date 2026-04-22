from django.db import models

from core.models import AbstractBaseModel


class ElGitSource(AbstractBaseModel):
    """Git 仓库源配置"""

    PLATFORM_CHOICES = (
        ("github", "GitHub"),
        ("gitee", "Gitee"),
        ("gitlab", "GitLab"),
    )

    name = models.CharField(max_length=128, unique=True, verbose_name="名称")
    platform = models.CharField(
        max_length=32,
        choices=PLATFORM_CHOICES,
        verbose_name="平台类型",
    )
    repo_url = models.URLField(verbose_name="仓库地址")
    token = models.CharField(max_length=512, verbose_name="Access Token")
    default_branch = models.CharField(
        max_length=128,
        default="main",
        verbose_name="默认分支",
    )
    description = models.TextField(default="", blank=True, verbose_name="备注")

    class Meta:
        db_table = "el_git_source"
        verbose_name = "仓库源"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"

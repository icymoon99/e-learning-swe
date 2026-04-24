from django.db import models
from core.models import AbstractBaseModel


SANDBOX_TYPES = (
    ("localdocker", "本地 Docker"),
    ("remotedocker", "远程 Docker"),
    ("localsystem", "本地系统"),
    ("remotesystem", "远程系统"),
)

STATUS_CHOICES = (
    ("active", "活跃"),
    ("inactive", "未激活"),
    ("error", "错误"),
)


class ElSandboxInstance(AbstractBaseModel):
    """沙箱实例模型"""

    name = models.CharField(max_length=128, verbose_name="沙箱名称")
    type = models.CharField(max_length=20, choices=SANDBOX_TYPES, verbose_name="沙箱类型")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="inactive",
        verbose_name="状态",
    )
    metadata = models.JSONField(default=dict, verbose_name="配置元信息")

    class Meta:
        db_table = "el_sandbox_instance"
        verbose_name = "沙箱实例"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

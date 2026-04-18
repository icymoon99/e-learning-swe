from django.db import models
from django.utils import timezone
from ulid_django.models import ULIDField
from ulid import ULID


class AbstractBaseModel(models.Model):
    """
    抽象基类模型，提供ULID作为主键和时间戳字段
    所有模型都应该继承这个类以确保一致的ID生成和时间戳记录
    """

    id = ULIDField(primary_key=True, editable=False, verbose_name="ID")
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    def save(self, *args, **kwargs):
        # 如果是新记录且没有ID，生成ULID
        if not self.pk and not self.id:
            self.id = str(ULID())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True  # 标记为抽象类，不会创建数据库表
        ordering = ["-created_at"]  # 默认按创建时间倒序排序

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

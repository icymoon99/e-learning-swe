from django.db import models
from django.contrib.auth.models import Group
from core.models import AbstractBaseModel


class ElMenu(AbstractBaseModel):
    """
    菜单模型 - 定义系统中的菜单结构
    支持多级菜单，通过 parent 字段建立层级关系
    """

    MENU_TYPE_CHOICES = [
        ('directory', '目录'),
        ('menu', '菜单'),
        ('button', '按钮'),
    ]

    name = models.CharField(max_length=50, unique=True, verbose_name="菜单标识")
    path = models.CharField(max_length=100, verbose_name="路由路径")
    component = models.CharField(max_length=100, blank=True, verbose_name="组件名称")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    title = models.CharField(max_length=50, verbose_name="显示标题")
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="父菜单"
    )
    order = models.IntegerField(default=0, verbose_name="排序")
    hidden = models.BooleanField(default=False, verbose_name="是否隐藏")
    keep_alive = models.BooleanField(default=False, verbose_name="是否缓存")
    permission = models.CharField(max_length=100, blank=True, verbose_name="权限标识")
    menu_type = models.CharField(
        max_length=20,
        choices=MENU_TYPE_CHOICES,
        default='menu',
        verbose_name="菜单类型"
    )

    class Meta(AbstractBaseModel.Meta):
        db_table = "el_system_menu"
        verbose_name = "菜单"
        verbose_name_plural = "菜单"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def to_tree_dict(self):
        """转换为树形字典结构"""
        result = {
            'id': str(self.id),
            'name': self.name,
            'path': self.path,
            'component': self.component,
            'icon': self.icon,
            'title': self.title,
            'order': self.order,
            'hidden': self.hidden,
            'keep_alive': self.keep_alive,
            'permission': self.permission,
            'menu_type': self.menu_type,
            'parent_id': str(self.parent_id) if self.parent else None,
        }

        children = self.children.all().order_by('order')
        if children.exists():
            result['children'] = [child.to_tree_dict() for child in children]

        return result


class ElGroupMenu(models.Model):
    """
    Django Group 与 ElMenu 的关联表
    使用 Django 内置的 Group 替代自定义 Role
    """
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name="用户组",
        related_name='group_menus'
    )
    menu = models.ForeignKey(
        ElMenu,
        on_delete=models.CASCADE,
        verbose_name="菜单"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "el_system_group_menu"
        verbose_name = "组菜单关联"
        verbose_name_plural = "组菜单关联"
        unique_together = ['group', 'menu']  # 防止重复关联

    def __str__(self):
        return f"{self.group.name} - {self.menu.title}"

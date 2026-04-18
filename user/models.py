from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from ulid import ULID
from core.models import AbstractBaseModel


class ElUserManager(BaseUserManager):
    """
    自定义用户管理器，用于创建ElUser实例
    支持使用用户名或手机号登录
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        创建并保存普通用户
        """
        if not username:
            raise ValueError(_("用户名不能为空"))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        创建并保存超级用户
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("超级用户必须设置is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("超级用户必须设置is_superuser=True"))

        return self.create_user(username, password, **extra_fields)


class ElUser(AbstractUser, AbstractBaseModel):
    """
    自定义用户模型，同时继承Django的AbstractUser和AbstractBaseModel
    添加昵称、手机号、头像字段，以及角色关联
    支持使用用户名或手机号登录
    从AbstractBaseModel继承ULID主键和时间戳字段
    """

    nickname = models.CharField(verbose_name=_("昵称"), max_length=50, blank=True)
    phone = models.CharField(
        verbose_name=_("手机号"), max_length=11, unique=True, null=True, blank=True
    )
    avatar = models.URLField(
        verbose_name=_("头像"), max_length=255, null=True, blank=True
    )
    # 使用 Django 内置的 groups 字段 (通过继承 AbstractUser) 替代自定义 roles

    # 使用自定义的用户管理器
    objects = ElUserManager()

    # 处理AbstractUser的date_joined字段与AbstractBaseModel的created_at字段冲突
    # 确保date_joined与created_at保持同步
    def save(self, *args, **kwargs):
        if not self.pk:
            # 如果是新创建的用户，确保date_joined和created_at一致
            if not self.id:  # 显式检查并设置 id
                self.id = str(ULID())
            self.date_joined = timezone.now()
        super().save(*args, **kwargs)

    class Meta(AbstractUser.Meta, AbstractBaseModel.Meta):
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
        swappable = "AUTH_USER_MODEL"
        db_table = "el_user"

    def __str__(self):
        return self.username or self.phone

    def get_menus(self):
        """
        获取用户的所有菜单（去重并排序）
        返回扁平化的菜单列表
        超级用户返回所有菜单
        使用 Django 内置的 groups 替代自定义 roles
        """
        from system.models import ElMenu, ElGroupMenu

        # 超级用户拥有所有菜单
        if self.is_superuser:
            return ElMenu.objects.all().order_by('order')

        menu_ids = set()
        # 通过 ElGroupMenu 关联获取用户所在组的菜单
        for group_menu in ElGroupMenu.objects.filter(group__in=self.groups.all()):
            menu = group_menu.menu
            menu_ids.add(menu.id)
            # 同时添加所有父菜单
            parent = menu.parent
            while parent:
                menu_ids.add(parent.id)
                parent = parent.parent

        menus = ElMenu.objects.filter(id__in=menu_ids).order_by('order')
        return menus

    def get_menu_tree(self):
        """
        获取用户的菜单树（只包含顶层菜单，子菜单嵌套）
        超级用户返回所有菜单树
        使用 Django 内置的 groups 替代自定义 roles
        """
        from system.models import ElMenu

        # 超级用户返回所有菜单
        if self.is_superuser:
            top_menus = ElMenu.objects.filter(parent=None).order_by('order')
            return [menu.to_tree_dict() for menu in top_menus]

        all_menus = self.get_menus()
        # 只获取顶层菜单
        top_menus = [m for m in all_menus if m.parent_id is None]
        return [menu.to_tree_dict() for menu in top_menus]

    def get_permissions(self):
        """
        获取用户的所有权限标识（去重）
        包括 Django 内置权限和菜单关联的权限
        """
        # 超级用户拥有所有权限
        if self.is_superuser:
            return ['*']

        # 使用 Django 内置的 get_all_permissions() 获取权限
        perms = set(self.get_all_permissions())

        # 添加菜单关联的权限
        from system.models import ElGroupMenu
        for group_menu in ElGroupMenu.objects.filter(group__in=self.groups.all()):
            if group_menu.menu.permission:
                perms.add(group_menu.menu.permission)

        return list(perms)

    def has_permission(self, permission_code):
        """
        检查用户是否拥有指定权限
        """
        if self.is_superuser or '*' in self.get_permissions():
            return True
        return permission_code in self.get_permissions()

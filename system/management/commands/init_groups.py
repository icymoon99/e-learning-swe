from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

from system.models import ElMenu, ElGroupMenu


class Command(BaseCommand):
    """
    初始化 Django Group 权限数据
    使用 Django 内置的 Group 替代自定义 Role
    """
    help = 'Initialize Django Group permission data with menus'

    def handle(self, *args, **kwargs):
        self.stdout.write('开始初始化 Django Group 权限数据...')
        self.init_groups()
        self.stdout.write(self.style.SUCCESS('Django Group 权限数据初始化完成！'))

    def init_groups(self):
        """初始化 Group 数据并关联菜单"""

        # 1. 超级管理员组
        super_admin, _ = Group.objects.get_or_create(name='超级管理员')

        # 为超级管理员关联所有菜单
        all_menus = ElMenu.objects.all()
        for menu in all_menus:
            ElGroupMenu.objects.get_or_create(group=super_admin, menu=menu)

        self.stdout.write(f'  组 "{super_admin.name}" 已配置，关联 {all_menus.count()} 个菜单')

        # 2. 普通管理员组
        admin, _ = Group.objects.get_or_create(name='普通管理员')

        # 普通管理员菜单 - 只保留前端存在的菜单
        admin_menu_names = [
            "user", "user:list", "user:detail",
            "math", "math:question", "math:setting"
        ]
        admin_menus = ElMenu.objects.filter(name__in=admin_menu_names)
        for menu in admin_menus:
            ElGroupMenu.objects.get_or_create(group=admin, menu=menu)

        self.stdout.write(f'  组 "{admin.name}" 已配置，关联 {admin_menus.count()} 个菜单')

        # 删除已不存在的菜单关联
        obsolete_menus = ElMenu.objects.filter(
            name__in=["dashboard", "course", "order", "system"]
        )
        if obsolete_menus.exists():
            deleted, _ = ElGroupMenu.objects.filter(menu__in=obsolete_menus).delete()
            if deleted:
                self.stdout.write(f'  清理了 {deleted} 个已删除菜单的关联')

        self.stdout.write(self.style.SUCCESS(f'  共创建/更新 {Group.objects.count()} 个 Group'))

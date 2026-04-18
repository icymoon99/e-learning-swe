from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from user.models import ElUser
from system.models import Role, Menu, GroupMenu


class Command(BaseCommand):
    """
    将自定义 RBAC 权限系统迁移到 Django 内置权限系统

    迁移内容：
    1. 为每个 Role 创建对应的 Django Group
    2. 同步 Role 的菜单关联到 GroupMenu
    3. 将用户的 roles 关联转换为 groups 关联
    """
    help = "Migrate from custom RBAC to Django built-in permissions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("开始迁移权限系统..."))

        # 1. 为每个 Role 创建对应的 Django Group
        self.stdout.write("\n1. 创建 Django Group...")
        migrated_count = 0
        for role in Role.objects.all():
            group, created = Group.objects.get_or_create(name=role.name)
            if created:
                self.stdout.write(f"   创建 Group: {group.name}")
            else:
                self.stdout.write(f"   已存在 Group: {group.name}")

            # 同步菜单关联到 GroupMenu
            for menu in role.menus.all():
                GroupMenu.objects.get_or_create(group=group, menu=menu)

            migrated_count += 1

        self.stdout.write(self.style.SUCCESS(f"   完成: {migrated_count} 个角色已迁移"))

        # 2. 将用户的 roles 关联转换为 groups 关联
        self.stdout.write("\n2. 迁移用户角色关联...")
        user_count = 0
        for user in ElUser.objects.filter(roles__isnull=False).distinct():
            for role in user.roles.all():
                try:
                    group = Group.objects.get(name=role.name)
                    user.groups.add(group)
                    self.stdout.write(f"   用户 {user.username} 添加到 Group: {group.name}")
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"   警告: Group {role.name} 不存在，跳过")
                    )
            user_count += 1

        self.stdout.write(self.style.SUCCESS(f"   完成: {user_count} 个用户已迁移"))

        # 3. 为超级用户设置 staff 和 superuser 标志（如果尚未设置）
        self.stdout.write("\n3. 检查超级用户权限...")
        admin_users = ElUser.objects.filter(roles__code='admin').distinct()
        for user in admin_users:
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(f"   用户 {user.username} 设置为超级管理员")

        # 4. 为普通 staff 用户设置 staff 标志
        self.stdout.write("\n4. 检查 Staff 用户权限...")
        staff_roles = Role.objects.exclude(code='admin')
        for role in staff_roles:
            for user in ElUser.objects.filter(roles=role).distinct():
                if not user.is_staff and not user.is_superuser:
                    user.is_staff = True
                    user.save()
                    self.stdout.write(f"   用户 {user.username} 设置为 Staff")

        self.stdout.write(self.style.SUCCESS("\n✓ 权限系统迁移完成！"))
        self.stdout.write("\n下一步:")
        self.stdout.write("  1. 生成迁移文件: python manage.py makemigrations")
        self.stdout.write("  2. 应用迁移: python manage.py migrate")
        self.stdout.write("  3. 运行测试: python manage.py test")

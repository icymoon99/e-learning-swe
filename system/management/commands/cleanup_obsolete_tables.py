from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    清理重构后遗留的过时数据库表
    system 和 user 应用已改用 Django 内置 Group 和 ElGroupMenu，需要删除旧表
    """
    help = 'Clean up obsolete tables after model refactoring (Permission, Role, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview tables to be dropped without executing',
        )

    def handle(self, *args, **kwargs):
        dry_run = kwargs['dry_run']

        # 需要清理的过时表列表（按依赖顺序，先清理外键关联表）
        obsolete_tables = [
            'el_system_role_permissions',  # Role-Permission 多对多关联表
            'el_system_role_menus',        # Role-Menu 多对多关联表
            'el_user_roles',               # User-Role 多对多关联表
            'el_system_role',              # 旧 Role 模型表
            'el_system_permission',        # 旧 Permission 模型表
        ]

        self.stdout.write('开始清理过时数据库表...')
        if dry_run:
            self.stdout.write(self.style.WARNING('【预览模式】不会实际删除表'))

        dropped_count = 0
        skipped_count = 0
        error_count = 0

        with connection.cursor() as cursor:
            # 获取当前数据库中实际存在的表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            for table in obsolete_tables:
                if table not in existing_tables:
                    self.stdout.write(f"  跳过: {table} (不存在)")
                    skipped_count += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  将要删除: {table}")
                    continue

                try:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
                    self.stdout.write(f"  已删除: {table}")
                    dropped_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  错误: 删除 {table} 失败 - {e}"))
                    error_count += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'预览完成！共 {len(obsolete_tables)} 个表待清理'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'清理完成！已删除 {dropped_count} 个表，跳过 {skipped_count} 个，错误 {error_count} 个'
            ))

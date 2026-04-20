from django.core.management.base import BaseCommand
from system.models import ElMenu


class Command(BaseCommand):
    """
    初始化菜单数据 - 只保留前端实际存在的菜单
    """
    help = 'Initialize menu data for frontend routes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to initialize menu data...')
        self.init_menus()
        self.stdout.write(self.style.SUCCESS('Menu data initialization completed!'))

    def init_menus(self):
        """Initialize menu data - only keep menus that exist in frontend"""

        # 1. User Management
        user_menu, _ = ElMenu.objects.get_or_create(
            name="user",
            defaults={
                "path": "/user",
                "title": "用户管理",
                "icon": "User",
                "order": 1,
                "permission": "user:view",
                "menu_type": "directory"
            }
        )

        ElMenu.objects.get_or_create(
            name="user:list",
            defaults={
                "path": "/user/list",
                "title": "用户列表",
                "parent": user_menu,
                "order": 1,
                "permission": "user:view",
                "menu_type": "menu"
            }
        )

        ElMenu.objects.get_or_create(
            name="user:detail",
            defaults={
                "path": "/user/detail/:id",
                "title": "用户详情",
                "parent": user_menu,
                "order": 2,
                "hidden": True,
                "permission": "user:detail",
                "menu_type": "menu"
            }
        )

        # 2. Math Management
        math_menu, _ = ElMenu.objects.get_or_create(
            name="math",
            defaults={
                "path": "/math",
                "title": "数学模块",
                "icon": "Grid",
                "order": 2,
                "permission": "math:view",
                "menu_type": "directory"
            }
        )

        ElMenu.objects.get_or_create(
            name="math:question",
            defaults={
                "path": "/math/question",
                "title": "试题管理",
                "parent": math_menu,
                "order": 1,
                "permission": "math:question:view",
                "menu_type": "menu"
            }
        )

        ElMenu.objects.get_or_create(
            name="math:setting",
            defaults={
                "path": "/math/setting",
                "title": "模块配置",
                "parent": math_menu,
                "order": 2,
                "permission": "math:setting:view",
                "menu_type": "menu"
            }
        )

        # 3. Sandbox Management
        sandbox_menu, _ = ElMenu.objects.get_or_create(
            name="sandbox",
            defaults={
                "path": "/sandbox",
                "title": "沙箱管理",
                "icon": "Monitor",
                "order": 3,
                "permission": "sandbox:view",
                "menu_type": "directory"
            }
        )

        ElMenu.objects.get_or_create(
            name="sandbox:instances",
            defaults={
                "path": "/sandbox/instances",
                "title": "实例列表",
                "parent": sandbox_menu,
                "order": 1,
                "permission": "sandbox:view",
                "menu_type": "menu"
            }
        )

        # 4. Agent Management
        agent_menu, _ = ElMenu.objects.get_or_create(
            name="agent",
            defaults={
                "path": "/agent",
                "title": "Agent管理",
                "icon": "Robot",
                "order": 4,
                "permission": "agent:view",
                "menu_type": "directory"
            }
        )

        ElMenu.objects.get_or_create(
            name="agent:list",
            defaults={
                "path": "/agent/list",
                "title": "Agent列表",
                "parent": agent_menu,
                "order": 1,
                "permission": "agent:view",
                "menu_type": "menu"
            }
        )

        ElMenu.objects.get_or_create(
            name="agent:execution",
            defaults={
                "path": "/agent/execution",
                "title": "执行日志",
                "parent": agent_menu,
                "order": 2,
                "permission": "agent:view",
                "menu_type": "menu"
            }
        )

        # Delete old menus that no longer exist in frontend
        old_menu_names = [
            "dashboard", "dashboard:home",
            "course", "course:list", "course:category", "course:detail",
            "order", "order:list", "order:refund", "order:detail",
            "system", "system:log", "system:config", "system:menu", "system:role"
        ]
        deleted_count, _ = ElMenu.objects.filter(name__in=old_menu_names).delete()
        if deleted_count:
            self.stdout.write(f'  Deleted {deleted_count} obsolete menu records')

        self.stdout.write(self.style.SUCCESS('Menus initialized!'))

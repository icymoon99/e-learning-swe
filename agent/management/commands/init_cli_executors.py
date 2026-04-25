"""注册预设的 CLI 执行器到数据库"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '将预设的 CLI 执行器注册到 ElExecutor 表（启动时自动调用）'

    def handle(self, *args, **options):
        from agent.models import ElExecutor

        ElExecutor.objects.get_or_create(
            code='trae',
            defaults={'name': 'Trae CLI', 'timeout': 3600, 'metadata': {}}
        )
        self.stdout.write(self.style.SUCCESS('已注册: Trae CLI'))

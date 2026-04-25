"""注册预设的 CLI 执行器"""
from django.core.management.base import BaseCommand
from sandbox.executors.base import ExecutorRegistry


class Command(BaseCommand):
    help = '注册预设的 CLI 执行器（启动时自动调用）'

    def handle(self, *args, **options):
        from sandbox.executors.trae_executor import TraeExecutor

        ExecutorRegistry.register(TraeExecutor())
        self.stdout.write(self.style.SUCCESS('已注册: Trae CLI'))

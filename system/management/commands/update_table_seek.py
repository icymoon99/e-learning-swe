import logging
import os

from django.core.management import BaseCommand, call_command
from django.core.management.base import CommandError
from django.db import connection, transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "执行数据初始化的脚本，按顺序执行以table_seek开头的命令文件"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            "--force",
            action="store_true",
            help="强制重新执行所有命令，忽略已执行记录",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅显示将要执行的命令，不实际执行",
        )

    @staticmethod
    def check_table_exists(table_name: str) -> bool:
        """检查表是否存在"""
        try:
            with connection.cursor() as cursor:
                tables = connection.introspection.table_names(cursor)
                return table_name in tables
        except Exception as e:
            logger.error(f"检查表 {table_name} 是否存在时发生错误: {str(e)}")
            return False

    def get_command_files(self, commands_dir: str) -> list[str]:
        """获取所有需要执行的命令文件"""
        try:
            if not os.path.exists(commands_dir):
                raise CommandError(f"Commands directory not found: {commands_dir}")

            # 获取所有.py文件并按名称排序
            command_files = sorted(
                [
                    f
                    for f in os.listdir(commands_dir)
                    if f.endswith(".py")
                    and f.startswith("table_seek")
                    and f != "__init__.py"
                ]
            )

            if not command_files:
                logger.warning("No table_seek commands found to execute")
                return []

            return command_files
        except Exception as e:
            logger.error(f"获取命令文件时发生错误: {str(e)}")
            raise CommandError(f"Failed to get command files: {str(e)}")

    def get_executed_commands(self) -> set[str]:
        """获取已成功执行的命令集合"""
        try:
            from system.models import SystemCommandsRecord

            executed_records = SystemCommandsRecord.objects.filter(
                status="success"
            ).values_list("name", flat=True)

            return set(executed_records)
        except Exception as e:
            logger.error(f"获取已执行命令记录时发生错误: {str(e)}")
            return set()

    def execute_command(self, command_name: str) -> bool:
        """执行单个命令并记录结果"""
        try:
            from system.models import SystemCommandsRecord

            logger.info(f"正在执行命令: {command_name}")

            # 使用事务确保命令执行和记录的原子性
            with transaction.atomic():
                # 执行命令
                _ = call_command(command_name)

                # 记录成功执行
                SystemCommandsRecord.objects.create(name=command_name, status="success")

            logger.info(f"命令 [{command_name}] 执行成功")
            return True

        except Exception as e:
            error_msg = f"执行命令 [{command_name}] 时发生错误: {str(e)}"
            logger.error(error_msg)
            # error_msg 已经通过 logger.error 记录，这里不需要重复输出

            # 记录失败执行
            try:
                from system.models import SystemCommandsRecord

                SystemCommandsRecord.objects.create(name=command_name, status="fail")
            except Exception as record_error:
                logger.error(f"记录命令执行失败状态时发生错误: {str(record_error)}")

            return False

    def handle(self, *args, **options):
        """主处理逻辑"""
        force = options.get("force", False)
        dry_run = options.get("dry_run", False)

        # 检查系统命令记录表是否存在
        if not self.check_table_exists("el_system_command_record"):
            raise CommandError(
                "表 el_system_command_record 不存在，请先运行数据库迁移: python manage.py migrate"
            )

        try:
            # 获取commands目录路径
            commands_dir = os.path.dirname(__file__)

            # 获取所有需要执行的命令文件
            command_files = self.get_command_files(commands_dir)
            if not command_files:
                return

            # 获取已执行的命令（如果不是强制模式）
            executed_commands = set() if force else self.get_executed_commands()

            # 统计信息
            total_commands = len(command_files)
            executed_count = 0
            skipped_count = 0
            failed_count = 0

            logger.info(f"发现 {total_commands} 个table_seek命令文件")

            if dry_run:
                logger.info("DRY RUN 模式 - 仅显示将要执行的命令")

            # 执行命令
            for command_file in command_files:
                # 去掉.py后缀，得到命令名
                command_name = command_file[:-3]

                if not force and command_name in executed_commands:
                    logger.info(f"命令 [{command_name}] 已成功执行，跳过...")
                    skipped_count += 1
                    continue

                if dry_run:
                    logger.info(f"将执行: {command_name}")
                    continue

                # 实际执行命令
                if self.execute_command(command_name):
                    executed_count += 1
                else:
                    failed_count += 1
                    # 如果命令执行失败，停止后续执行
                    logger.error("命令执行失败，停止后续命令执行")
                    break

            # 输出执行统计
            if not dry_run:
                logger.info(
                    f"执行完成！统计信息：\n"
                    f"- 总命令数: {total_commands}\n"
                    f"- 成功执行: {executed_count}\n"
                    f"- 跳过执行: {skipped_count}\n"
                    f"- 执行失败: {failed_count}"
                )
            else:
                logger.info(f"DRY RUN 完成，共发现 {total_commands} 个命令")

        except CommandError:
            # CommandError 已经包含了用户友好的错误信息，直接重新抛出
            raise
        except ImportError as e:
            error_msg = f"导入 SystemCommandsRecord 模型失败: {str(e)}"
            logger.error(error_msg)
            raise CommandError(error_msg)
        except Exception as e:
            error_msg = f"初始化命令执行失败: {str(e)}"
            logger.error(error_msg)
            raise CommandError(error_msg)

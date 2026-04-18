import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from en_word_learn.models import ElEnWordCategory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "初始化ElEnWordCategory表的种子数据"

    def handle(self, *args, **options):
        """执行种子数据初始化"""
        try:
            created_count = 0
            updated_count = 0

            # 种子数据
            seed_data = [
                {
                    "id": "01K67QTFH1MTE4CA2B0966T8KJ",
                    "name": "小学",
                    "order": 10,
                    "thumbnail_url": "",
                    "created_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857418, tzinfo=timezone.get_current_timezone()),
                    "updated_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857556, tzinfo=timezone.get_current_timezone()),
                },
                {
                    "id": "01K67QTFH1HYCFGQ9W01QY8WH4",
                    "name": "初中",
                    "order": 20,
                    "thumbnail_url": "",
                    "created_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857438, tzinfo=timezone.get_current_timezone()),
                    "updated_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857577, tzinfo=timezone.get_current_timezone()),
                },
                {
                    "id": "01K67QTFH1F54W1M86HM2E5D41",
                    "name": "高中",
                    "order": 30,
                    "thumbnail_url": "",
                    "created_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857447, tzinfo=timezone.get_current_timezone()),
                    "updated_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857591, tzinfo=timezone.get_current_timezone()),
                },
                {
                    "id": "01K67QTFH14AS9TYJ1HCFK0QRY",
                    "name": "CYLE",
                    "order": 40,
                    "thumbnail_url": "",
                    "created_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857455, tzinfo=timezone.get_current_timezone()),
                    "updated_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857602, tzinfo=timezone.get_current_timezone()),
                },
                {
                    "id": "01K67QTFH10BCGRQRRVKYV1XB1",
                    "name": "MSE",
                    "order": 50,
                    "thumbnail_url": "",
                    "created_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857462, tzinfo=timezone.get_current_timezone()),
                    "updated_at": timezone.datetime(2025, 9, 28, 16, 42, 53, 857613, tzinfo=timezone.get_current_timezone()),
                },
            ]

            # 逐条处理种子数据，实现upsert逻辑
            for data in seed_data:
                category, created = ElEnWordCategory.objects.update_or_create(
                    id=data["id"],
                    defaults={
                        "name": data["name"],
                        "order": data["order"],
                        "thumbnail_url": data["thumbnail_url"],
                        "updated_at": timezone.now(),
                    }
                )
                
                if created:
                    # 如果是新创建的记录，设置created_at
                    category.created_at = data["created_at"]
                    category.save(update_fields=["created_at"])
                    created_count += 1
                    logger.info(f"创建新记录: {category.name} (ID: {category.id})")
                else:
                    updated_count += 1
                    logger.info(f"更新记录: {category.name} (ID: {category.id})")

            # 输出统计信息
            total_count = created_count + updated_count
            result_msg = f"处理完成 - 创建: {created_count} 条，更新: {updated_count} 条，总计: {total_count} 条ElEnWordCategory记录"
            logger.info(result_msg)

        except Exception as e:
            error_msg = f"初始化ElEnWordCategory种子数据失败: {str(e)}"
            logger.error(error_msg)
            raise e
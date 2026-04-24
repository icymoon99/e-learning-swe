from django.core.management.base import BaseCommand

from llm.constants import PRESET_PROVIDERS
from llm.models import ElLLMProvider, ElLLMModel


class Command(BaseCommand):
    help = "初始化预置 LLM 供应商和模型数据（幂等）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="强制更新已存在的供应商和模型（以预置数据覆盖）",
        )

    def handle(self, *args, **options):
        force = options["force"]
        total_providers = 0
        created_providers = 0
        skipped_providers = 0
        total_models = 0

        for code, data in PRESET_PROVIDERS.items():
            provider, created = ElLLMProvider.objects.get_or_create(
                code=code,
                defaults={
                    "name": data["name"],
                    "base_url": data["base_url"],
                },
            )
            total_providers += 1

            if created:
                created_providers += 1
                self.stdout.write(f"  创建供应商: {data['name']} ({code})")
            else:
                if force:
                    provider.name = data["name"]
                    provider.base_url = data["base_url"]
                    provider.save(update_fields=["name", "base_url", "updated_at"])
                    self.stdout.write(f"  更新供应商: {data['name']} ({code})")
                else:
                    skipped_providers += 1
                    self.stdout.write(f"  跳过供应商: {data['name']} ({code})")

            # 处理模型
            for model_data in data["models"]:
                model, model_created = ElLLMModel.objects.get_or_create(
                    provider=provider,
                    model_code=model_data["model_code"],
                    defaults={
                        "display_name": model_data["display_name"],
                        "context_window": model_data["context_window"],
                        "max_output_tokens": model_data["max_output_tokens"],
                    },
                )
                total_models += 1

                if model_created:
                    self.stdout.write(f"    创建模型: {model_data['display_name']}")
                elif force:
                    model.display_name = model_data["display_name"]
                    model.context_window = model_data["context_window"]
                    model.max_output_tokens = model_data["max_output_tokens"]
                    model.save(
                        update_fields=[
                            "display_name",
                            "context_window",
                            "max_output_tokens",
                            "updated_at",
                        ]
                    )
                    self.stdout.write(f"    更新模型: {model_data['display_name']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"初始化完成: 共 {total_providers} 个供应商，"
                f"创建 {created_providers} 个，跳过 {skipped_providers} 个，"
                f"共 {total_models} 个模型"
            )
        )

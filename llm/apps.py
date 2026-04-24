from django.apps import AppConfig


class LlmConfig(AppConfig):
    default_auto_field = "django.core.fields.BigAutoField"
    name = "llm"
    verbose_name = "大模型配置"

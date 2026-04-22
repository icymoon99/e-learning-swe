from django.apps import AppConfig


class GitSourceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "git_source"
    verbose_name = "仓库源管理"

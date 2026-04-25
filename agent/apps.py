from django.apps import AppConfig


class AgentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agent'
    verbose_name = "Agent 管理"

    def ready(self):
        from agent import signals  # noqa
        from agent.signals import register_builtin_executors
        register_builtin_executors()

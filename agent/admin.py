from django.contrib import admin
from agent.models import ElAgent, ElAgentExecutionLog


@admin.register(ElAgent)
class ElAgentAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "model", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["code", "name"]


@admin.register(ElAgentExecutionLog)
class ElAgentExecutionLogAdmin(admin.ModelAdmin):
    list_display = ["agent", "thread_id", "status", "created_at"]
    list_filter = ["status", "agent"]
    search_fields = ["thread_id", "agent__name"]

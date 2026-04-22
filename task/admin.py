from django.contrib import admin

from .models import ElTask, ElTaskConversation


@admin.register(ElTask)
class ElTaskAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "git_source", "source_branch", "created_at"]
    list_filter = ["status"]
    search_fields = ["title", "description"]


@admin.register(ElTaskConversation)
class ElTaskConversationAdmin(admin.ModelAdmin):
    list_display = ["task", "comment_type", "agent_code", "created_at"]
    list_filter = ["comment_type"]

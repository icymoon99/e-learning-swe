from django.contrib import admin

from .models import ElGitSource


@admin.register(ElGitSource)
class ElGitSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "platform", "repo_url", "default_branch", "created_at"]
    list_filter = ["platform"]
    search_fields = ["name", "repo_url"]

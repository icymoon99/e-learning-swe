from django.contrib import admin

from sandbox.models import ElSandboxInstance


@admin.register(ElSandboxInstance)
class ElSandboxInstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "root_path", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("name", "root_path")

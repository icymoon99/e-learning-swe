from django.contrib import admin

from sandbox.models import ElSandboxInstance


@admin.register(ElSandboxInstance)
class ElSandboxInstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("name",)

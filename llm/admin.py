from django.contrib import admin
from llm.models import ElLLMProvider, ElLLMModel


@admin.register(ElLLMProvider)
class ElLLMProviderAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "enabled", "created_at")
    list_filter = ("enabled",)
    search_fields = ("code", "name")


@admin.register(ElLLMModel)
class ElLLMModelAdmin(admin.ModelAdmin):
    list_display = ("model_code", "display_name", "provider", "enabled", "sort_order")
    list_filter = ("enabled", "provider")
    search_fields = ("model_code", "display_name")

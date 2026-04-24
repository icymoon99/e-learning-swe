from django.urls import path, include
from rest_framework.routers import DefaultRouter

from llm.views import ElLLMProviderViewSet, ElLLMModelViewSet

router = DefaultRouter()
router.register(r"providers", ElLLMProviderViewSet, basename="llmprovider")
router.register(r"models", ElLLMModelViewSet, basename="llmmodel")

urlpatterns = [
    path("", include(router.urls)),
]

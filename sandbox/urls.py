from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sandbox.views import SandboxInstanceViewSet

router = DefaultRouter()
router.register(r"instances", SandboxInstanceViewSet, basename="sandbox-instance")

urlpatterns = [
    path("", include(router.urls)),
]

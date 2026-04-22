from django.urls import path, include
from rest_framework.routers import DefaultRouter

from git_source.views import GitSourceViewSet

router = DefaultRouter()
router.register(r"sources", GitSourceViewSet, basename="gitsource")

urlpatterns = [
    path("", include(router.urls)),
]

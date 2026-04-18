from django.urls import path, include
from rest_framework.routers import DefaultRouter

from q2.views.task_view import TaskViewSet
from q2.views.failure_view import FailureViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"failures", FailureViewSet, basename="failure")

urlpatterns = [
    path("", include(router.urls)),
]

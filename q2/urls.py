from django.urls import path, include
from rest_framework.routers import DefaultRouter

from q2.views.task_view import TaskViewSet
from q2.views.failure_view import FailureViewSet
from q2.views.schedule_view import ScheduleViewSet
from q2.views.queue_view import QueueViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"failures", FailureViewSet, basename="failure")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
router.register(r"queue", QueueViewSet, basename="queue")

urlpatterns = [
    path("", include(router.urls)),
]

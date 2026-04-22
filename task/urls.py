from django.urls import path, include
from rest_framework.routers import DefaultRouter

from task.views import TaskViewSet, ConversationViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "tasks/<str:task_pk>/conversations/",
        ConversationViewSet.as_view({"get": "list", "post": "create"}),
    ),
]

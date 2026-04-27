from django.urls import path, include
from rest_framework.routers import DefaultRouter

from agent.views import AgentViewSet, AgentExecutionLogViewSet, ExecutorViewSet

router = DefaultRouter()
router.register(r"agents", AgentViewSet)
router.register(r"execution-logs", AgentExecutionLogViewSet)
router.register(r"executors", ExecutorViewSet, basename="executor")

urlpatterns = [
    path("", include(router.urls)),
]

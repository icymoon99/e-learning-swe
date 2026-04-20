from django.urls import path, include
from rest_framework.routers import DefaultRouter

from agent.views import AgentViewSet, AgentExecutionLogViewSet

router = DefaultRouter()
router.register(r"agents", AgentViewSet)
router.register(r"execution-logs", AgentExecutionLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

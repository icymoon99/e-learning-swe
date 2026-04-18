from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.user_view import UserViewSet
from .views.token_view import CustomTokenObtainPairView, CustomTokenRefreshView

router = DefaultRouter()
router.register(r"admin/users", UserViewSet, basename="user")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
] + router.urls

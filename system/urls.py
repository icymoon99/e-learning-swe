from rest_framework.routers import DefaultRouter

from .views.menu_view import MenuViewSet
from .views.group_view import GroupViewSet

router = DefaultRouter()
router.register(r"admin/menus", MenuViewSet, basename="menu")
router.register(r"admin/groups", GroupViewSet, basename="group")

urlpatterns = router.urls

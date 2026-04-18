from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from system.models import ElMenu
from system.serializers import MenuSerializer, MenuTreeSerializer


class MenuViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ElMenu.objects.all().order_by("order", "created_at")
    serializer_class = MenuSerializer

    def list(self, request, *args, **kwargs):
        menus = request.user.get_menu_tree()
        return ApiResponse.ok(content={"results": menus})

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request, *args, **kwargs):
        menus = ElMenu.objects.filter(parent=None).order_by("order")
        serializer = MenuTreeSerializer(menus, many=True)
        return ApiResponse.ok(content={"results": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return ApiResponse.ok(content=serializer.data)
        return ApiResponse.parameter_error(message=serializer.errors)

    def _get_instance(self, pk):
        try:
            return ElMenu.objects.get(pk=pk)
        except ElMenu.DoesNotExist:
            raise ApiException(msg="菜单不存在", code=ResponseStatus.NOT_FOUND.code)

    def retrieve(self, request, *args, **kwargs):
        menu = self._get_instance(kwargs["pk"])
        serializer = MenuSerializer(menu)
        return ApiResponse.ok(content=serializer.data)

    def update(self, request, *args, **kwargs):
        menu = self._get_instance(kwargs["pk"])
        serializer = MenuSerializer(menu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.ok(content=serializer.data)
        return ApiResponse.parameter_error(message=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        menu = self._get_instance(kwargs["pk"])
        menu.delete()
        return ApiResponse.ok(message="删除成功", http_status=status.HTTP_200_OK)

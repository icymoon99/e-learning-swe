from django.contrib.auth.models import Group
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from system.serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    Django Group 管理视图集
    用于替代自定义的 RoleViewSet
    """
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer

    def list(self, request, *args, **kwargs):
        """获取组列表"""
        groups = self.get_queryset()
        serializer = GroupSerializer(groups, many=True)
        return ApiResponse.ok(content={"count": len(serializer.data), "results": serializer.data})

    def create(self, request, *args, **kwargs):
        """创建组"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return ApiResponse.ok(content=serializer.data)
        return ApiResponse.parameter_error(message=serializer.errors)

    def _get_instance(self, pk):
        """获取组实例"""
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            raise ApiException(msg="组不存在", code=ResponseStatus.NOT_FOUND.code)

    def retrieve(self, request, *args, **kwargs):
        """获取组详情"""
        group = self._get_instance(kwargs["pk"])
        serializer = GroupSerializer(group)
        return ApiResponse.ok(content=serializer.data)

    def update(self, request, *args, **kwargs):
        """更新组"""
        group = self._get_instance(kwargs["pk"])
        serializer = GroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.ok(content=serializer.data)
        return ApiResponse.parameter_error(message=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除组"""
        group = self._get_instance(kwargs["pk"])
        group.delete()
        return ApiResponse.ok(message="删除成功", http_status=status.HTTP_200_OK)

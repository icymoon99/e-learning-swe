from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from ..serializers import UserDetailSerializer, UserListSerializer, UserCreateSerializer
from ..models import ElUser


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ElUser.objects.all().order_by("-created_at")

    @action(detail=False, methods=["get"], url_path="profile")
    def profile(self, request, *args, **kwargs):
        serializer = UserDetailSerializer(request.user)
        return ApiResponse.ok(content=serializer.data)

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        search = request.query_params.get("search")
        if search:
            users = users.filter(
                Q(username__icontains=search)
                | Q(nickname__icontains=search)
                | Q(phone__icontains=search)
            )
        return paginated_response(request, users, UserListSerializer)

    def _get_instance(self, pk):
        try:
            return ElUser.objects.get(pk=pk)
        except ElUser.DoesNotExist:
            raise ApiException(msg="用户不存在", code=ResponseStatus.NOT_FOUND.code)

    def retrieve(self, request, *args, **kwargs):
        user = self._get_instance(kwargs["pk"])
        serializer = UserDetailSerializer(user)
        return ApiResponse.ok(content=serializer.data)

    def update(self, request, *args, **kwargs):
        user = self._get_instance(kwargs["pk"])
        if user.is_superuser and not request.user.is_superuser:
            return ApiResponse.unauthorized(message="无权修改超级用户")

        # 检查是否有组分配权限
        group_ids = request.data.get('group_ids')
        if group_ids is not None:
            # 只有超级管理员可以分配组
            if not request.user.is_superuser:
                return ApiResponse.unauthorized(message="只有超级管理员可以分配组")

            # 无法给普通用户类型（非staff且非superuser）分配组
            if not user.is_staff and not user.is_superuser:
                return ApiResponse.parameter_error(message="普通用户类型无法分配组")

        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponse.ok(content=serializer.data)
        return ApiResponse.parameter_error(message=serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = self._get_instance(kwargs["pk"])
        if user.id == request.user.id:
            return ApiResponse.parameter_error(message="不能删除自己")

        if user.is_superuser and not request.user.is_superuser:
            return ApiResponse.unauthorized(message="无权删除超级用户")

        user.delete()
        return ApiResponse.ok(message="删除成功", http_status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return ApiResponse.ok(content=UserDetailSerializer(user).data)
        return ApiResponse.parameter_error(message=serializer.errors)

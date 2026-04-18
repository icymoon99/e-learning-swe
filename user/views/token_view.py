from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.common.exception.api_response import ApiResponse
from core.common.utils.aes_utils import aes_decrypt


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 从 attrs 中获取加密的密码
        password = attrs.get("password")

        # 如果密码存在，则进行解密
        if password:
            attrs["password"] = aes_decrypt(password)

        data = super().validate(attrs)
        # 这里可以添加额外的用户信息到 token 中
        # data['username'] = self.user.username
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return ApiResponse.ok(content=serializer.validated_data)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return ApiResponse.ok(content=serializer.validated_data)

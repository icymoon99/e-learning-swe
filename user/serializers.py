from rest_framework import serializers
from .models import ElUser


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器（基础版）"""
    class Meta:
        model = ElUser
        fields = [
            "id",
            "username",
            "nickname",
            "phone",
            "avatar",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器（包含菜单和权限）"""
    menus = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),  # Django Group 使用整数 ID
        write_only=True,
        required=False
    )
    groups = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = ElUser
        fields = [
            "id",
            "username",
            "nickname",
            "phone",
            "avatar",
            "is_superuser",
            "is_staff",
            "user_type",
            "menus",
            "permissions",
            "group_ids",
            "groups",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_user_type(self, obj):
        """获取用户类型"""
        if obj.is_superuser:
            return "super_admin"
        elif obj.is_staff:
            return "staff"
        else:
            return "normal"

    def get_menus(self, obj):
        """获取用户的菜单树"""
        return obj.get_menu_tree()

    def get_permissions(self, obj):
        """获取用户的权限标识列表"""
        return obj.get_permissions()

    def get_groups(self, obj):
        """获取用户的组列表（替代原来的角色）"""
        return [
            {"id": str(group.id), "name": group.name}
            for group in obj.groups.all()
        ]

    def update(self, instance, validated_data):
        group_ids = validated_data.pop('group_ids', None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新组关联（使用 Django 内置 Group）
        if group_ids is not None:
            from django.contrib.auth.models import Group
            groups = Group.objects.filter(id__in=group_ids)
            instance.groups.set(groups)

        return instance


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    groups = serializers.SerializerMethodField()

    class Meta:
        model = ElUser
        fields = [
            "id",
            "username",
            "nickname",
            "phone",
            "avatar",
            "groups",
            "created_at",
        ]

    def get_groups(self, obj):
        """获取用户的组列表"""
        return [
            {"id": str(group.id), "name": group.name}
            for group in obj.groups.all()
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),  # Django Group 使用整数 ID
        write_only=True,
        required=False
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ElUser
        fields = [
            "username",
            "nickname",
            "phone",
            "avatar",
            "password",
            "group_ids",
        ]

    def create(self, validated_data):
        group_ids = validated_data.pop('group_ids', [])
        password = validated_data.pop('password')

        user = ElUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # 关联 Django 组
        if group_ids:
            from django.contrib.auth.models import Group
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)

        return user

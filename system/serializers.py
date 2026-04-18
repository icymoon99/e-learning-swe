from rest_framework import serializers
from django.contrib.auth.models import Group

from system.models import ElMenu


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_id = serializers.CharField(source="parent.id", read_only=True, allow_null=True)

    class Meta:
        model = ElMenu
        fields = [
            "id",
            "name",
            "path",
            "component",
            "icon",
            "title",
            "parent_id",
            "order",
            "hidden",
            "keep_alive",
            "permission",
            "menu_type",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by("order")
        if children.exists():
            return MenuSerializer(children, many=True).data
        return []


class MenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = ElMenu
        fields = [
            "id",
            "name",
            "path",
            "icon",
            "title",
            "order",
            "hidden",
            "permission",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by("order")
        if children.exists():
            return MenuTreeSerializer(children, many=True).data
        return []


class GroupSerializer(serializers.ModelSerializer):
    """Django Group 序列化器 - 替代自定义 Role"""
    menu_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    menus = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'menu_ids', 'menus']
        read_only_fields = ['id']

    def get_menus(self, obj):
        """获取组关联的菜单"""
        from system.models import ElGroupMenu
        group_menus = ElGroupMenu.objects.filter(group=obj).select_related('menu')
        return [
            {
                'id': str(gm.menu.id),
                'name': gm.menu.name,
                'title': gm.menu.title,
                'path': gm.menu.path,
            }
            for gm in group_menus
        ]

    def create(self, validated_data):
        from system.models import ElGroupMenu
        menu_ids = validated_data.pop('menu_ids', [])
        group = Group.objects.create(**validated_data)

        # 关联菜单
        if menu_ids:
            menus = ElMenu.objects.filter(id__in=menu_ids)
            for menu in menus:
                ElGroupMenu.objects.get_or_create(group=group, menu=menu)

        return group

    def update(self, instance, validated_data):
        from system.models import ElGroupMenu
        menu_ids = validated_data.pop('menu_ids', None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新菜单关联
        if menu_ids is not None:
            menus = ElMenu.objects.filter(id__in=menu_ids)
            # 清除旧的关联
            ElGroupMenu.objects.filter(group=instance).delete()
            # 创建新的关联
            for menu in menus:
                ElGroupMenu.objects.get_or_create(group=instance, menu=menu)

        return instance

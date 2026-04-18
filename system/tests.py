"""
System应用API测试
测试系统管理相关接口（菜单、组）
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import Group

from user.models import ElUser
from system.models import ElMenu, ElGroupMenu


class MenuAPITestCase(TestCase):
    """菜单管理API测试"""

    def setUp(self):
        """测试前准备"""
        self.admin = ElUser.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        # 创建测试菜单
        self.menu = ElMenu.objects.create(
            name='test_menu',
            title='测试菜单',
            path='/test',
            order=1,
            menu_type='directory'
        )

    def test_menu_list(self):
        """测试菜单列表接口"""
        from system.views.menu_view import MenuViewSet

        factory = APIRequestFactory()
        request = factory.get('/api/system/admin/menus/all/')
        force_authenticate(request, user=self.admin)

        view = MenuViewSet.as_view({'get': 'all'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('results', response.data['content'])

    def test_menu_create(self):
        """测试创建菜单"""
        from system.views.menu_view import MenuViewSet

        factory = APIRequestFactory()
        request = factory.post('/api/system/admin/menus/', {
            'name': 'new_menu',
            'title': '新菜单',
            'path': '/new',
            'order': 2,
            'menu_type': 'menu'
        })
        force_authenticate(request, user=self.admin)

        view = MenuViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)

        # 验证菜单已创建
        self.assertTrue(ElMenu.objects.filter(name='new_menu').exists())

    def test_menu_detail(self):
        """测试菜单详情接口"""
        from system.views.menu_view import MenuViewSet

        factory = APIRequestFactory()
        request = factory.get(f'/api/system/admin/menus/{self.menu.id}/')
        force_authenticate(request, user=self.admin)

        view = MenuViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=str(self.menu.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertEqual(response.data['content']['name'], 'test_menu')


class GroupAPITestCase(TestCase):
    """Django Group 管理API测试"""

    def setUp(self):
        """测试前准备"""
        self.admin = ElUser.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        # 创建测试组
        self.group = Group.objects.create(name='测试组')

    def test_group_list(self):
        """测试组列表接口"""
        from system.views.group_view import GroupViewSet

        factory = APIRequestFactory()
        request = factory.get('/api/system/admin/groups/')
        force_authenticate(request, user=self.admin)

        view = GroupViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('results', response.data['content'])

    def test_group_create(self):
        """测试创建组"""
        from system.views.group_view import GroupViewSet

        factory = APIRequestFactory()
        request = factory.post('/api/system/admin/groups/', {
            'name': '新组',
        })
        force_authenticate(request, user=self.admin)

        view = GroupViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)

        # 验证组已创建
        self.assertTrue(Group.objects.filter(name='新组').exists())

    def test_group_detail(self):
        """测试组详情接口"""
        from system.views.group_view import GroupViewSet

        factory = APIRequestFactory()
        request = factory.get(f'/api/system/admin/groups/{self.group.id}/')
        force_authenticate(request, user=self.admin)

        view = GroupViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.group.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertEqual(response.data['content']['name'], '测试组')


class MenuModelTestCase(TestCase):
    """菜单模型测试"""

    def setUp(self):
        """测试前准备"""
        self.parent_menu = ElMenu.objects.create(
            name='parent',
            title='父菜单',
            path='/parent',
            order=1,
            menu_type='directory'
        )
        self.child_menu = ElMenu.objects.create(
            name='child',
            title='子菜单',
            path='/child',
            order=1,
            menu_type='menu',
            parent=self.parent_menu
        )

    def test_menu_to_tree_dict(self):
        """测试菜单转换为树形字典"""
        tree = self.parent_menu.to_tree_dict()
        self.assertEqual(tree['name'], 'parent')
        self.assertEqual(len(tree['children']), 1)
        self.assertEqual(tree['children'][0]['name'], 'child')


class GroupMenuModelTestCase(TestCase):
    """组菜单关联模型测试"""

    def setUp(self):
        """测试前准备"""
        self.group = Group.objects.create(name='test_group')
        self.menu = ElMenu.objects.create(
            name='test_menu',
            title='测试菜单',
            path='/test',
            order=1,
            menu_type='directory'
        )

    def test_group_menu_association(self):
        """测试组菜单关联"""
        group_menu = ElGroupMenu.objects.create(group=self.group, menu=self.menu)
        self.assertEqual(str(group_menu), f"{self.group.name} - {self.menu.title}")
        self.assertIn(self.menu, [gm.menu for gm in self.group.group_menus.all()])

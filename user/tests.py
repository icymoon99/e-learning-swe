"""
User应用API测试
测试用户认证和管理相关接口
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from user.models import ElUser
from system.models import ElMenu, ElGroupMenu


class UserAPITestCase(TestCase):
    """用户API测试"""

    def setUp(self):
        """测试前准备 - 使用 Django 内置 Group 替代自定义 Role"""
        from django.contrib.auth.models import Group

        # 先创建 admin Group
        self.admin_group = Group.objects.create(name='超级管理员')

        # 创建测试用户
        self.user = ElUser.objects.create_user(
            username='test_user',
            password='test123'
        )
        # 创建超级用户
        self.admin = ElUser.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        # 分配超级管理员组
        self.admin.groups.add(self.admin_group)

    def test_login_success(self):
        """测试登录成功 - 使用加密密码"""
        from user.views.token_view import CustomTokenObtainPairView
        from core.common.utils.aes_utils import aes_encrypt

        # 加密密码
        encrypted_password = aes_encrypt('admin123')

        factory = APIRequestFactory()
        request = factory.post('/api/user/token/', {
            'username': 'admin',
            'password': encrypted_password
        })

        view = CustomTokenObtainPairView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('access', response.data['content'])
        self.assertIn('refresh', response.data['content'])

    def test_user_profile(self):
        """测试获取用户资料"""
        from user.views.user_view import UserViewSet

        factory = APIRequestFactory()
        request = factory.get('/api/user/admin/users/profile/')
        force_authenticate(request, user=self.admin)

        view = UserViewSet.as_view({'get': 'profile'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertEqual(response.data['content']['username'], 'admin')
        self.assertIn('menus', response.data['content'])
        self.assertIn('permissions', response.data['content'])

    def test_user_list(self):
        """测试用户列表接口"""
        from user.views.user_view import UserViewSet

        factory = APIRequestFactory()
        request = factory.get('/api/user/admin/users/')
        force_authenticate(request, user=self.admin)

        view = UserViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('results', response.data['content'])

    def test_user_create(self):
        """测试创建用户"""
        from user.views.user_view import UserViewSet

        factory = APIRequestFactory()
        request = factory.post('/api/user/admin/users/', {
            'username': 'new_user',
            'password': 'newpass123',
            'nickname': '新用户'
        })
        force_authenticate(request, user=self.admin)

        view = UserViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 0)
        self.assertEqual(response.data['content']['username'], 'new_user')

        # 验证用户已创建
        self.assertTrue(ElUser.objects.filter(username='new_user').exists())


class UserModelTestCase(TestCase):
    """用户模型测试"""

    def setUp(self):
        """测试前准备 - 使用 Django 内置 Group 替代自定义 Role"""
        from django.contrib.auth.models import Group

        self.user = ElUser.objects.create_user(
            username='test_user',
            password='test123'
        )
        # 创建 Django Group
        self.group = Group.objects.create(
            name='测试组'
        )
        # 创建菜单
        self.menu = ElMenu.objects.create(
            name='test_menu',
            path='/test',
            title='测试菜单'
        )
        # 关联 Group 和 Menu
        ElGroupMenu.objects.create(group=self.group, menu=self.menu)
        # 分配用户到组
        self.user.groups.add(self.group)

    def test_user_get_permissions(self):
        """测试获取用户权限"""
        permissions = self.user.get_permissions()
        self.assertIsInstance(permissions, list)

    def test_user_get_menu_tree(self):
        """测试获取用户菜单树"""
        menus = self.user.get_menu_tree()
        self.assertIsInstance(menus, list)

    def test_user_has_permission(self):
        """测试权限检查"""
        # 超级用户拥有所有权限
        self.user.is_superuser = True
        self.user.save()
        self.assertTrue(self.user.has_permission('any:permission'))

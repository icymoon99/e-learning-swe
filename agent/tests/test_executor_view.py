from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from agent.models import ElExecutor

User = get_user_model()


class TestExecutorViewSet(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', is_superuser=True
        )
        self.executor = ElExecutor.objects.create(
            code='trae', name='Trae CLI', enabled=True, timeout=3600,
            metadata={"env_vars": {"TRAECLI_PERSONAL_ACCESS_TOKEN": "sk-123"}, "cli_args": {}},
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_executors(self):
        """GET 列表返回所有执行器"""
        url = reverse('executor-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['code'], 0)
        results = data['content']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['code'], 'trae')

    def test_retrieve_executor(self):
        """GET 详情返回带 schema 合并的数据"""
        url = reverse('executor-detail', kwargs={'pk': self.executor.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('metadata_schema', data['content'])
        self.assertIn('env_vars', data['content']['metadata_schema'])

    def test_update_executor_enabled(self):
        """PUT 可以修改 enabled 字段"""
        url = reverse('executor-detail', kwargs={'pk': self.executor.id})
        data = {
            'enabled': False,
            'metadata_schema_input': {
                'env_vars': {
                    'TRAECLI_PERSONAL_ACCESS_TOKEN': {
                        'type': 'password', 'required': True,
                        'label': 'Personal Access Token', 'hint': 'Trae CLI 鉴权令牌',
                        'value': 'new-token',
                    },
                },
                'cli_args': {},
            },
        }
        resp = self.client.put(url, data, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.executor.refresh_from_db()
        self.assertFalse(self.executor.enabled)
        self.assertEqual(
            self.executor.metadata['env_vars']['TRAECLI_PERSONAL_ACCESS_TOKEN'],
            'new-token',
        )

    def test_create_disabled(self):
        """POST 创建被禁用"""
        url = reverse('executor-list')
        resp = self.client.post(url, {'code': 'new', 'name': 'New'}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)

    def test_delete_disabled(self):
        """DELETE 删除被禁用"""
        url = reverse('executor-detail', kwargs={'pk': self.executor.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 405)

    def test_types_action(self):
        """GET /executors/types/ 返回所有 schema"""
        url = reverse('executor-types')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('trae', data['content'])

    def test_unauthenticated_access(self):
        """未认证用户无法访问"""
        self.client.force_authenticate(user=None)
        url = reverse('executor-list')
        resp = self.client.get(url)
        self.assertIn(resp.status_code, [401, 403])

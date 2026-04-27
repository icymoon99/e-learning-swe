from django.test import TestCase
from agent.models import ElExecutor
from agent.serializers import ExecutorSerializer


class TestExecutorSerializer(TestCase):
    def setUp(self):
        self.executor = ElExecutor.objects.create(
            code='trae',
            name='Trae CLI',
            enabled=True,
            timeout=3600,
            metadata={
                "env_vars": {"TRAECLI_PERSONAL_ACCESS_TOKEN": "sk-test-123"},
                "cli_args": {},
            },
        )

    def test_list_fields(self):
        """序列化器包含所有期望字段"""
        serializer = ExecutorSerializer(self.executor)
        data = serializer.data
        expected_keys = {'id', 'code', 'name', 'enabled', 'timeout', 'metadata_schema'}
        self.assertEqual(set(data.keys()), expected_keys)

    def test_metadata_schema_merges_value(self):
        """GET 时 metadata_schema 合并 schema 定义 + DB 值"""
        serializer = ExecutorSerializer(self.executor)
        data = serializer.data
        schema = data['metadata_schema']
        env_vars = schema['env_vars']
        self.assertIn('TRAECLI_PERSONAL_ACCESS_TOKEN', env_vars)
        self.assertEqual(
            env_vars['TRAECLI_PERSONAL_ACCESS_TOKEN']['value'],
            'sk-test-123'
        )

    def test_metadata_schema_empty_value(self):
        """DB 中不存在的字段，value 为空字符串"""
        # 使用 trae 代码但不设置 metadata 值
        executor2 = ElExecutor.objects.create(
            code='test_exec2',
            name='Test',
            enabled=True,
            timeout=1800,
            metadata={},
        )
        # 手动覆盖 code 为 trae 来测试 schema 合并（因 code 唯一，先删后建）
        executor2.delete()
        self.executor.metadata = {}
        self.executor.save()
        serializer = ExecutorSerializer(self.executor)
        data = serializer.data
        schema = data['metadata_schema']
        env_vars = schema['env_vars']
        self.assertEqual(
            env_vars['TRAECLI_PERSONAL_ACCESS_TOKEN']['value'],
            ''
        )

    def test_update_enabled(self):
        """update 方法可以修改 enabled"""
        serializer = ExecutorSerializer(
            self.executor,
            data={'enabled': False, 'metadata_schema': self.executor.metadata},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertFalse(instance.enabled)

    def test_update_metadata_extract_values(self):
        """update 时从 metadata_schema_input 提取 value 存回 metadata"""
        update_data = {
            'enabled': True,
            'metadata_schema_input': {
                'env_vars': {
                    'TRAECLI_PERSONAL_ACCESS_TOKEN': {
                        'type': 'password',
                        'required': True,
                        'label': 'Personal Access Token',
                        'hint': 'Trae CLI 鉴权令牌',
                        'value': 'new-token-value',
                    },
                },
                'cli_args': {},
            },
        }
        serializer = ExecutorSerializer(self.executor, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 重新从 DB 获取最新值
        self.executor.refresh_from_db()
        self.assertEqual(
            self.executor.metadata['env_vars']['TRAECLI_PERSONAL_ACCESS_TOKEN'],
            'new-token-value',
        )

    def test_read_only_fields(self):
        """code, name, timeout 为只读字段"""
        serializer = ExecutorSerializer(
            self.executor,
            data={
                'code': 'new_code',
                'name': 'New Name',
                'timeout': 9999,
                'enabled': True,
                'metadata_schema': {},
            },
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        self.assertEqual(instance.code, 'trae')
        self.assertEqual(instance.name, 'Trae CLI')
        self.assertEqual(instance.timeout, 3600)

from django.test import TestCase
from agent.schemas import EXECUTOR_SCHEMAS, get_executor_schema, get_all_executor_schemas


class TestExecutorSchemas(TestCase):
    def test_trae_schema_exists(self):
        """trae 执行器 schema 存在"""
        self.assertIn('trae', EXECUTOR_SCHEMAS)

    def test_trae_schema_structure(self):
        """trae schema 包含 env_vars 和 cli_args 分组"""
        schema = EXECUTOR_SCHEMAS['trae']
        self.assertIn('env_vars', schema)
        self.assertIn('cli_args', schema)

    def test_trae_env_var_fields(self):
        """trae env_vars 字段包含 type/required/label/hint"""
        env_vars = EXECUTOR_SCHEMAS['trae']['env_vars']
        for key, field in env_vars.items():
            self.assertIn('type', field)
            self.assertIn('required', field)
            self.assertIn('label', field)
            self.assertIn('hint', field)

    def test_get_executor_schema_returns_value(self):
        """get_executor_schema 返回指定类型的 schema"""
        schema = get_executor_schema('trae')
        self.assertEqual(schema, EXECUTOR_SCHEMAS['trae'])

    def test_get_executor_schema_unknown_raises(self):
        """未知类型抛出 ValueError"""
        with self.assertRaises(ValueError):
            get_executor_schema('unknown')

    def test_get_all_executor_schemas(self):
        """get_all_executor_schemas 返回所有 schema"""
        result = get_all_executor_schemas()
        self.assertIn('trae', result)

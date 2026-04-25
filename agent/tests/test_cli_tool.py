"""CLI Tool 工厂测试"""
import unittest
from unittest.mock import MagicMock, patch

from sandbox.executors.base import CLIExecutor, ExecutorRegistry, ExecutorResult
from agent.tools.cli_tool import create_cli_tool


class MockCLIExecutor(CLIExecutor):
    code = 'mock'
    name = 'Mock'

    def build_command(self, query, session_id=None, **kwargs):
        return ['mock', '--query', query]

    def parse_output(self, raw_output):
        return ExecutorResult(
            success=True, session_id='sid-1',
            output='mock 完成', files_changed=['a.py', 'b.py'],
        )


class TestCreateCLITool(unittest.TestCase):
    def setUp(self):
        self._prev = ExecutorRegistry._registry.copy()
        ExecutorRegistry.register(MockCLIExecutor())
        self.mock_backend = MagicMock()

    def tearDown(self):
        ExecutorRegistry._registry = self._prev

    def test_tool_name_is_code_workshop(self):
        tool = create_cli_tool('mock', self.mock_backend)
        self.assertEqual(tool.name, 'code_workshop')

    def test_tool_invokes_executor(self):
        tool = create_cli_tool('mock', self.mock_backend)
        self.mock_backend.execute.return_value = MagicMock(
            output='{"status": "success", "message": "ok"}'
        )
        result = tool.invoke({'query': '实现XX功能', 'session_id': None})
        self.assertIn('CLI 执行成功', result)
        self.assertIn('a.py', result)

    def test_tool_reports_failure(self):
        # MockCLIExecutor 的 parse_output 固定返回 success，
        # 改用 Mock 覆盖 parse_output 行为来模拟失败
        original = ExecutorRegistry.get('mock')
        ExecutorRegistry._registry['mock'] = MagicMock(
            spec=CLIExecutor, code='mock', name='Mock',
            build_command=original.build_command,
            parse_output=lambda raw: ExecutorResult(
                success=False, session_id=None,
                output='', files_changed=[], error='超时',
            ),
        )
        tool = create_cli_tool('mock', self.mock_backend)
        self.mock_backend.execute.return_value = MagicMock(output='{"status": "error"}')
        result = tool.invoke({'query': '实现XX功能', 'session_id': None})
        self.assertIn('CLI 执行失败', result)
        self.assertIn('超时', result)
        # 恢复原 mock
        ExecutorRegistry._registry['mock'] = original

    def test_unknown_executor_raises(self):
        with self.assertRaises(KeyError):
            create_cli_tool('unknown', self.mock_backend)

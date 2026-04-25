"""Trae CLI 执行器插件测试"""
import unittest

from sandbox.executors.trae_executor import TraeExecutor, TRAEOCL_QUERY_SUFFIX


class TestTraeExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = TraeExecutor()

    def test_code_and_name(self):
        self.assertEqual(self.executor.code, 'trae')
        self.assertEqual(self.executor.name, 'Trae CLI')

    def test_build_command_new_session(self):
        cmd = self.executor.build_command("实现XX功能")
        self.assertEqual(cmd[0], 'traecli')
        self.assertIn('--session-id', cmd)
        self.assertIn('--yolo', cmd)
        self.assertIn('--json', cmd)
        self.assertIn('--print', cmd)
        self.assertIn('--query-timeout', cmd)
        self.assertIn('--query', cmd)
        # query 参数应该包含约束后缀
        query_idx = cmd.index('--query')
        self.assertIn('【重要】', cmd[query_idx + 1])

    def test_build_command_resume_session(self):
        cmd = self.executor.build_command("继续修改", session_id="task-abc123")
        resume_idx = cmd.index('--resume')
        self.assertEqual(cmd[resume_idx + 1], 'task-abc123')
        self.assertNotIn('--session-id', cmd)

    def test_build_command_custom_timeout(self):
        cmd = self.executor.build_command("测试", timeout=1800)
        timeout_idx = cmd.index('--query-timeout')
        self.assertEqual(cmd[timeout_idx + 1], '1800')

    def test_parse_output_success_from_json_block(self):
        raw = '''开始工作...
一些自然语言输出
```json
{
  "summary": "完成了用户注册接口",
  "files_changed": ["user/views.py", "user/urls.py"],
  "status": "success"
}
```
'''
        result = self.executor.parse_output(raw)
        self.assertTrue(result.success)
        self.assertEqual(result.output, '完成了用户注册接口')
        self.assertEqual(result.files_changed, ['user/views.py', 'user/urls.py'])
        self.assertIsNone(result.error)

    def test_parse_output_error_from_json_block(self):
        raw = '''```json
{
  "summary": "编译失败：缺少依赖",
  "files_changed": [],
  "status": "error"
}
```
'''
        result = self.executor.parse_output(raw)
        self.assertFalse(result.success)
        self.assertEqual(result.error, '编译失败：缺少依赖')

    def test_parse_output_cli_json_fallback(self):
        # 没有 ```json 块时，回退解析 CLI 自身 JSON
        raw = '{"status": "success", "session_id": "sid-1", "message": "done"}'
        result = self.executor.parse_output(raw)
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'done')

    def test_parse_output_invalid_json(self):
        raw = '这不是 JSON'
        result = self.executor.parse_output(raw)
        self.assertFalse(result.success)
        self.assertEqual(result.error, '无法解析执行结果')

    def test_parse_output_invalid_json_block(self):
        raw = '```json\n{ invalid json }\n```'
        result = self.executor.parse_output(raw)
        # 应回退到 CLI JSON 解析，仍然失败
        self.assertFalse(result.success)

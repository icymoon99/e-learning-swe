import unittest
from sandbox.backends.base import _sanitize_env


class TestSanitizeEnv(unittest.TestCase):
    def test_valid_env_passes_through(self):
        env = {"MY_VAR": "value", "TRAECLI_TOKEN": "tk-123"}
        result = _sanitize_env(env)
        self.assertEqual(result, {"MY_VAR": "value", "TRAECLI_TOKEN": "tk-123"})

    def test_none_returns_empty(self):
        self.assertEqual(_sanitize_env(None), {})

    def test_empty_dict_returns_empty(self):
        self.assertEqual(_sanitize_env({}), {})

    def test_protected_keys_blocked(self):
        env = {"PATH": "/hacked", "SHELL": "/bin/zsh", "SAFE": "ok"}
        result = _sanitize_env(env)
        self.assertNotIn("PATH", result)
        self.assertNotIn("SHELL", result)
        self.assertEqual(result["SAFE"], "ok")

    def test_invalid_key_pattern_blocked(self):
        env = {"rm -rf": "bad", "FOO BAR": "bad", "123KEY": "bad"}
        result = _sanitize_env(env)
        self.assertEqual(result, {})

    def test_value_converted_to_string(self):
        env = {"NUM_VAR": 42}
        result = _sanitize_env(env)
        self.assertEqual(result, {"NUM_VAR": "42"})

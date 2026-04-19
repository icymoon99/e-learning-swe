"""AES 工具函数测试 — 自定义 key/iv 版本"""
import base64
import unittest

from core.common.utils.aes_utils import aes_encrypt_with_key, aes_decrypt_with_key


class TestAESWithKey(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        """加密后解密，应还原原文"""
        key = b"0123456789abcdef"  # 16 字节
        iv = b"fedcba9876543210"
        original = "hello sandbox"

        encrypted = aes_encrypt_with_key(original, key, iv)
        self.assertIsInstance(encrypted, str)

        decrypted = aes_decrypt_with_key(encrypted, key, iv)
        self.assertEqual(original, decrypted)

    def test_different_key_decrypt_fails(self):
        """错误密钥解密应抛异常"""
        key = b"0123456789abcdef"
        iv = b"fedcba9876543210"
        wrong_key = b"abcdef0123456789"

        encrypted = aes_encrypt_with_key("secret", key, iv)
        with self.assertRaises(Exception):
            aes_decrypt_with_key(encrypted, wrong_key, iv)

    def test_encrypted_output_is_base64_string(self):
        """加密输出应为 base64 字符串"""
        key = b"testkey123456789"
        iv = b"testiv1234567890"
        encrypted = aes_encrypt_with_key("test", key, iv)
        # base64 解码不应抛异常
        base64.b64decode(encrypted)

    def test_empty_string_encrypt(self):
        """空字符串加密后应能正常解密"""
        key = b"0123456789abcdef"
        iv = b"fedcba9876543210"
        encrypted = aes_encrypt_with_key("", key, iv)
        decrypted = aes_decrypt_with_key(encrypted, key, iv)
        self.assertEqual("", decrypted)

    def test_unicode_string_encrypt(self):
        """Unicode 字符串加密后应能正常解密"""
        key = b"0123456789abcdef"
        iv = b"fedcba9876543210"
        original = "沙箱配置密码 123"
        encrypted = aes_encrypt_with_key(original, key, iv)
        decrypted = aes_decrypt_with_key(encrypted, key, iv)
        self.assertEqual(original, decrypted)


if __name__ == "__main__":
    unittest.main()

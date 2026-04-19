import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def aes_encrypt(plain_text: str) -> str:
    """
    AES/CBC/PKCS7 加密
    :param plain_text: 原始字符串
    :return: base64 编码的加密字符串
    """
    # 直接从环境变量获取 KEY 和 IV
    key_str = os.getenv("AES_KEY")
    iv_str = os.getenv("AES_IV")

    if not key_str or not iv_str:
        raise ValueError("AES_KEY 或 AES_IV 环境变量未设置")

    key = key_str.encode("utf-8")
    iv = iv_str.encode("utf-8")

    # 使用 PKCS7 填充
    padded_text = pad(plain_text.encode("utf-8"), AES.block_size)

    # 加密
    generator = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = generator.encrypt(padded_text)

    # 返回 base64 编码的字符串
    return base64.b64encode(encrypted_bytes).decode("utf-8")
def aes_decrypt(encoded_text: str) -> str:
    """
    AES/CBC/PKCS7 解密
    :param encoded_text: base64 编码的加密字符串
    :return: 解密后的原始字符串
    """
    # 直接从环境变量获取 KEY 和 IV
    key_str = os.getenv("AES_KEY")
    iv_str = os.getenv("AES_IV")

    if not key_str or not iv_str:
        raise ValueError("AES_KEY 或 AES_IV 环境变量未设置")

    key = key_str.encode("utf-8")
    iv = iv_str.encode("utf-8")

    generator = AES.new(key, AES.MODE_CBC, iv)
    encoded_text_bytes = base64.b64decode(encoded_text)

    # 解密
    decrypted_bytes = generator.decrypt(encoded_text_bytes)

    # 使用 unpad 去除 PKCS7 填充
    original_text_bytes = unpad(decrypted_bytes, AES.block_size)

def aes_encrypt_with_key(plain_text: str, key: bytes, iv: bytes) -> str:
    """
    AES/CBC/PKCS7 加密（自定义 key/iv）
    :param plain_text: 原始字符串
    :param key: AES 密钥（16/24/32 字节）
    :param iv: 初始化向量（16 字节）
    :return: base64 编码的加密字符串
    """
    padded_text = pad(plain_text.encode("utf-8"), AES.block_size)
    generator = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = generator.encrypt(padded_text)
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def aes_decrypt_with_key(encoded_text: str, key: bytes, iv: bytes) -> str:
    """
    AES/CBC/PKCS7 解密（自定义 key/iv）
    :param encoded_text: base64 编码的加密字符串
    :param key: AES 密钥（16/24/32 字节）
    :param iv: 初始化向量（16 字节）
    :return: 解密后的原始字符串
    """
    generator = AES.new(key, AES.MODE_CBC, iv)
    encoded_text_bytes = base64.b64decode(encoded_text)
    decrypted_bytes = generator.decrypt(encoded_text_bytes)
    original_text_bytes = unpad(decrypted_bytes, AES.block_size)
    return original_text_bytes.decode("utf-8")

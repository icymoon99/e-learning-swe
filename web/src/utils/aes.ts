import CryptoJS from 'crypto-js'

const AES_KEY = import.meta.env.VITE_AES_KEY || 'aH5aH5bG0dC6aA3oN0cK4aU5jU6aK2lN'
const AES_IV = import.meta.env.VITE_AES_IV || 'hK6eB4aE1aF3gH5q'

/**
 * AES 加密 (CBC 模式, PKCS7 填充)
 * 与 Django 后端解密对齐
 */
export function encryptAES(text: string): string {
  const key = CryptoJS.enc.Utf8.parse(AES_KEY)
  const iv = CryptoJS.enc.Utf8.parse(AES_IV)

  const encrypted = CryptoJS.AES.encrypt(text, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })

  return encrypted.toString()
}

/**
 * AES 解密
 */
export function decryptAES(encryptedText: string): string {
  const key = CryptoJS.enc.Utf8.parse(AES_KEY)
  const iv = CryptoJS.enc.Utf8.parse(AES_IV)

  const decrypted = CryptoJS.AES.decrypt(encryptedText, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })

  return decrypted.toString(CryptoJS.enc.Utf8)
}

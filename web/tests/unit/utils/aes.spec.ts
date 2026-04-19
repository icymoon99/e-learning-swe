import { describe, it, expect } from 'vitest'
import { encryptAES, decryptAES } from '@/utils/aes'

describe('aes', () => {
  describe('encryptAES', () => {
    it('should encrypt a plain text string', () => {
      const encrypted = encryptAES('hello world')
      expect(encrypted).toBeDefined()
      expect(typeof encrypted).toBe('string')
      expect(encrypted).not.toBe('hello world')
    })

    it('should produce different ciphertext for different inputs', () => {
      const enc1 = encryptAES('password1')
      const enc2 = encryptAES('password2')
      expect(enc1).not.toBe(enc2)
    })
  })

  describe('decryptAES', () => {
    it('should decrypt back to original plaintext', () => {
      const original = 'hello world'
      const encrypted = encryptAES(original)
      const decrypted = decryptAES(encrypted)
      expect(decrypted).toBe(original)
    })

    it('should handle Chinese characters', () => {
      const original = '你好世界'
      const encrypted = encryptAES(original)
      const decrypted = decryptAES(encrypted)
      expect(decrypted).toBe(original)
    })

    it('should handle JSON strings', () => {
      const original = '{"username":"admin","password":"123456"}'
      const encrypted = encryptAES(original)
      const decrypted = decryptAES(encrypted)
      expect(decrypted).toBe(original)
    })
  })
})

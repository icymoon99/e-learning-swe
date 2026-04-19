import { describe, it, expect } from 'vitest'
import { validateUsername, validatePassword } from '@/utils/validate'

describe('validate', () => {
  describe('validateUsername', () => {
    it('should return true for valid username (>= 2 chars)', () => {
      expect(validateUsername('admin')).toBe(true)
      expect(validateUsername('ab')).toBe(true)
    })

    it('should return false for short username (< 2 chars)', () => {
      expect(validateUsername('a')).toBe(false)
      expect(validateUsername('')).toBe(false)
    })

    it('should return false for whitespace-only username', () => {
      expect(validateUsername('   ')).toBe(false)
    })
  })

  describe('validatePassword', () => {
    it('should return true for valid password (>= 6 chars)', () => {
      expect(validatePassword('123456')).toBe(true)
      expect(validatePassword('longpassword')).toBe(true)
    })

    it('should return false for short password (< 6 chars)', () => {
      expect(validatePassword('12345')).toBe(false)
      expect(validatePassword('')).toBe(false)
    })
  })
})

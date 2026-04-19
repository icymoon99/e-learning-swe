import { describe, it, expect } from 'vitest'
import { getTypeTagType, getStatusTagType } from '@/utils/sandbox'

describe('sandbox utils', () => {
  describe('getTypeTagType', () => {
    it('should return primary for localdocker', () => {
      expect(getTypeTagType('localdocker')).toBe('primary')
    })

    it('should return warning for remotedocker', () => {
      expect(getTypeTagType('remotedocker')).toBe('warning')
    })

    it('should return success for localsystem', () => {
      expect(getTypeTagType('localsystem')).toBe('success')
    })

    it('should return info for remotesystem (empty maps to info fallback)', () => {
      expect(getTypeTagType('remotesystem')).toBe('info')
    })
  })

  describe('getStatusTagType', () => {
    it('should return success for active', () => {
      expect(getStatusTagType('active')).toBe('success')
    })

    it('should return info for inactive', () => {
      expect(getStatusTagType('inactive')).toBe('info')
    })

    it('should return danger for error', () => {
      expect(getStatusTagType('error')).toBe('danger')
    })
  })
})

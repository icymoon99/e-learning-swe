import { describe, it, expect } from 'vitest'
import { formatDateTime, formatDate } from '@/utils/format'

describe('format', () => {
  describe('formatDateTime', () => {
    it('should format a Date object to default format', () => {
      const date = new Date('2026-04-18T12:30:45')
      expect(formatDateTime(date)).toBe('2026-04-18 12:30:45')
    })

    it('should format a date string', () => {
      expect(formatDateTime('2026-04-18T12:30:45')).toBe('2026-04-18 12:30:45')
    })

    it('should support custom format', () => {
      const date = new Date('2026-04-18T12:30:45')
      expect(formatDateTime(date, 'YYYY/MM/DD HH:mm')).toBe('2026/04/18 12:30')
    })
  })

  describe('formatDate', () => {
    it('should format to date only', () => {
      const date = new Date('2026-04-18T12:30:45')
      expect(formatDate(date)).toBe('2026-04-18')
    })
  })
})

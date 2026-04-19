import { describe, it, expect, beforeEach } from 'vitest'
import { storage } from '@/utils/storage'

const PREFIX = 'el_swe_'

describe('storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('set', () => {
    it('should store a string value with prefix', () => {
      storage.set('token', 'abc123')
      expect(localStorage.getItem(`${PREFIX}token`)).toBe('"abc123"')
    })

    it('should store an object value', () => {
      storage.set('user', { id: '1', name: 'admin' })
      expect(localStorage.getItem(`${PREFIX}user`)).toBe('{"id":"1","name":"admin"}')
    })

    it('should store a number value', () => {
      storage.set('expires', 1234567890)
      expect(localStorage.getItem(`${PREFIX}expires`)).toBe('1234567890')
    })
  })

  describe('get', () => {
    it('should retrieve a stored string value', () => {
      storage.set('name', 'test')
      expect(storage.get<string>('name')).toBe('test')
    })

    it('should retrieve a stored object value', () => {
      storage.set('user', { id: '1', name: 'admin' })
      expect(storage.get('user')).toEqual({ id: '1', name: 'admin' })
    })

    it('should return null for non-existent key', () => {
      expect(storage.get('nonexistent')).toBeNull()
    })

    it('should return null for malformed JSON', () => {
      localStorage.setItem(`${PREFIX}bad`, '{invalid json}')
      expect(storage.get('bad')).toBeNull()
    })
  })

  describe('remove', () => {
    it('should remove a specific key', () => {
      storage.set('a', '1')
      storage.set('b', '2')
      storage.remove('a')
      expect(storage.get('a')).toBeNull()
      expect(storage.get('b')).toBe('2')
    })
  })

  describe('clear', () => {
    it('should clear all localStorage items', () => {
      storage.set('a', '1')
      storage.set('b', '2')
      storage.clear()
      expect(storage.get('a')).toBeNull()
      expect(storage.get('b')).toBeNull()
    })
  })
})

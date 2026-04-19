import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { storage } from '@/utils/storage'

// Mock API layer
vi.mock('@/api/auth', () => ({
  loginApi: vi.fn(),
  refreshTokenApi: vi.fn(),
}))

import * as authApi from '@/api/auth'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    storage.clear()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should be not authenticated with empty tokens', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
      expect(store.accessToken).toBe('')
    })

    it('should restore tokens from storage on init', () => {
      storage.set('access_token', 'restored_access')
      storage.set('refresh_token', 'restored_refresh')
      storage.set('token_expires_at', Date.now() + 3600000)

      const store = useAuthStore()
      expect(store.accessToken).toBe('restored_access')
      expect(store.refreshToken).toBe('restored_refresh')
      expect(store.isAuthenticated).toBe(true)
    })
  })

  describe('setTokens / clearTokens', () => {
    it('should set tokens in state and storage', () => {
      const store = useAuthStore()
      store.setTokens({
        access: 'new_access',
        refresh: 'new_refresh',
      })

      expect(store.accessToken).toBe('new_access')
      expect(store.isAuthenticated).toBe(true)
      expect(storage.get('access_token')).toBe('new_access')
    })

    it('should clear all tokens from state and storage', () => {
      const store = useAuthStore()
      store.setTokens({ access: 'a', refresh: 'r' })
      store.clearTokens()

      expect(store.accessToken).toBe('')
      expect(store.isAuthenticated).toBe(false)
      expect(storage.get('access_token')).toBeNull()
    })
  })

  describe('isTokenExpiringSoon', () => {
    it('should return true when token expires in less than 5 minutes', () => {
      const store = useAuthStore()
      store.tokenExpiresAt = Date.now() + 3 * 60 * 1000
      expect(store.isTokenExpiringSoon).toBe(true)
    })

    it('should return false when token has plenty of time', () => {
      const store = useAuthStore()
      store.tokenExpiresAt = Date.now() + 24 * 60 * 60 * 1000
      expect(store.isTokenExpiringSoon).toBe(false)
    })
  })

  describe('login', () => {
    it('should set tokens on successful login', async () => {
      vi.mocked(authApi.loginApi).mockResolvedValue({
        data: {
          code: 0,
          message: '成功',
          content: {
            access: 'jwt_access_token',
            refresh: 'jwt_refresh_token',
          },
        },
      } as any)

      const store = useAuthStore()
      const result = await store.login({ username: 'admin', password: '123456' })

      expect(result).toBe(true)
      expect(store.accessToken).toBe('jwt_access_token')
    })

    it('should throw error on failed login', async () => {
      vi.mocked(authApi.loginApi).mockResolvedValue({
        data: {
          code: 1,
          message: '用户名或密码错误',
          content: null,
        },
      } as any)

      const store = useAuthStore()
      await expect(store.login({ username: 'admin', password: 'wrong' }))
        .rejects.toThrow('用户名或密码错误')
    })
  })

  describe('refreshAccessToken', () => {
    it('should refresh tokens successfully', async () => {
      vi.mocked(authApi.refreshTokenApi).mockResolvedValue({
        data: {
          code: 0,
          message: '成功',
          content: {
            access: 'new_access',
            refresh: 'new_refresh',
          },
        },
      } as any)

      const store = useAuthStore()
      store.refreshToken = 'existing_refresh'

      const token = await store.refreshAccessToken()
      expect(token).toBe('new_access')
      expect(store.accessToken).toBe('new_access')
    })

    it('should throw if no refresh token available', async () => {
      const store = useAuthStore()
      await expect(store.refreshAccessToken()).rejects.toThrow('No refresh token available')
    })
  })

  describe('logout', () => {
    it('should clear all auth-related state', () => {
      const store = useAuthStore()
      store.setTokens({ access: 'a', refresh: 'r' })
      store.logout()

      expect(store.accessToken).toBe('')
      expect(store.refreshToken).toBe('')
    })
  })
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TokenPair, LoginCredentials } from '@/types/auth'
import { loginApi, refreshTokenApi } from '@/api/auth'
import { usePermissionStore } from './permission'
import { useUserStore } from './user'
import { storage } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string>(storage.get<string>('access_token') || '')
  const refreshToken = ref<string>(storage.get<string>('refresh_token') || '')
  const tokenExpiresAt = ref<number>(storage.get<number>('token_expires_at') || 0)

  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value && tokenExpiresAt.value > Date.now()
  })

  const isTokenExpiringSoon = computed(() => {
    const fiveMinutes = 5 * 60 * 1000
    return tokenExpiresAt.value - Date.now() < fiveMinutes
  })

  // Actions
  const setTokens = (tokens: TokenPair) => {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    tokenExpiresAt.value = Date.now() + 24 * 60 * 60 * 1000

    storage.set('access_token', tokens.access)
    storage.set('refresh_token', tokens.refresh)
    storage.set('token_expires_at', tokenExpiresAt.value)
  }

  const clearTokens = () => {
    accessToken.value = ''
    refreshToken.value = ''
    tokenExpiresAt.value = 0

    storage.remove('access_token')
    storage.remove('refresh_token')
    storage.remove('token_expires_at')
  }

  const login = async (credentials: LoginCredentials) => {
    const { data } = await loginApi(credentials)
    if (data.code === 0 && data.content) {
      setTokens({
        access: data.content.access,
        refresh: data.content.refresh,
      })
      return true
    }
    throw new Error(data.message || '登录失败')
  }

  const refreshAccessToken = async (): Promise<string> => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const { data } = await refreshTokenApi(refreshToken.value)
      if (data.code === 0 && data.content) {
        setTokens({
          access: data.content.access,
          refresh: data.content.refresh,
        })
        return data.content.access
      }
      throw new Error('Token refresh failed')
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  const logout = () => {
    clearTokens()
    const permissionStore = usePermissionStore()
    const userStore = useUserStore()
    permissionStore.clear()
    userStore.clearUserInfo()
  }

  return {
    accessToken,
    refreshToken,
    tokenExpiresAt,
    isAuthenticated,
    isTokenExpiringSoon,
    setTokens,
    clearTokens,
    login,
    refreshAccessToken,
    logout,
  }
})

import { post } from '@/utils/request'
import { encryptAES } from '@/utils/aes'
import type { LoginCredentials, LoginResponse, TokenPair } from '@/types/auth'

/**
 * 登录（密码 AES 加密）
 */
export function loginApi(credentials: LoginCredentials) {
  return post<LoginResponse>('/user/token/', {
    username: credentials.username,
    password: encryptAES(credentials.password),
  })
}

/**
 * 刷新 Token
 */
export function refreshTokenApi(refreshToken: string) {
  return post<TokenPair>('/user/token/refresh/', {
    refresh: refreshToken,
  })
}

/**
 * 登出
 */
export function logoutApi() {
  return post('/user/logout/')
}

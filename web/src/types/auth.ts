// Token 对
export interface TokenPair {
  access: string
  refresh: string
}

// 登录凭证
export interface LoginCredentials {
  username: string
  password: string
}

// 登录响应（content 字段）
export interface LoginResponse {
  access: string
  refresh: string
}

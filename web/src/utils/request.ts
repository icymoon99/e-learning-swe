import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { decryptAES } from './aes'
import { storage } from './storage'
import type { ApiResponse } from '@/types/api'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 附加 JWT Token
    const token = storage.get<string>('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 登录接口的密码已在 API 层单独通过 AES 加密，此处不需要处理

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response

    // 如果响应体是加密的，解密
    const encryptedFlag = response.headers['encrypted-flag']
    if (encryptedFlag === 'true' && typeof data === 'string') {
      return { ...response, data: JSON.parse(decryptAES(data)) }
    }

    return response
  },
  (error) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          // Token 失效，清除并跳转登录
          storage.remove('access_token')
          storage.remove('refresh_token')
          storage.remove('token_expires_at')
          window.location.href = `/login?redirect=${window.location.pathname}`
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  },
)

// 便捷方法
export function get<T = unknown>(url: string, config?: AxiosRequestConfig) {
  return request.get<ApiResponse<T>>(url, config)
}

export function post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) {
  return request.post<ApiResponse<T>>(url, data, config)
}

export function put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) {
  return request.put<ApiResponse<T>>(url, data, config)
}

export function del<T = unknown>(url: string, config?: AxiosRequestConfig) {
  return request.delete<ApiResponse<T>>(url, config)
}

export default request

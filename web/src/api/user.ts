import { get, post, put, del } from '@/utils/request'
import type { UserInfo } from '@/types/user'
import type { PaginatedResponse, ListParams } from '@/types/api'

/**
 * 获取当前用户信息
 */
export function getUserProfileApi() {
  return get<UserInfo>('/user/admin/users/profile/')
}

/**
 * 获取用户列表
 */
export function getUserListApi(params?: ListParams) {
  return get<PaginatedResponse<UserInfo>>('/user/users/', { params })
}

/**
 * 获取用户详情
 */
export function getUserDetailApi(id: string) {
  return get<UserInfo>(`/user/users/${id}/`)
}

/**
 * 创建用户
 */
export function createUserApi(data: Partial<UserInfo>) {
  return post<UserInfo>('/user/users/', data)
}

/**
 * 更新用户
 */
export function updateUserApi(id: string, data: Partial<UserInfo>) {
  return put<UserInfo>(`/user/users/${id}/`, data)
}

/**
 * 删除用户
 */
export function deleteUserApi(id: string) {
  return del(`/user/users/${id}/`)
}

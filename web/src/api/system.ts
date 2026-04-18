import { get, post, put, del } from '@/utils/request'
import type { Menu } from '@/types/system'

/**
 * 获取菜单列表
 */
export function getMenuListApi() {
  return get<Menu[]>('/system/menus/')
}

/**
 * 获取菜单详情
 */
export function getMenuDetailApi(id: string) {
  return get<Menu>(`/system/menus/${id}/`)
}

/**
 * 创建菜单
 */
export function createMenuApi(data: Partial<Menu>) {
  return post<Menu>('/system/menus/', data)
}

/**
 * 更新菜单
 */
export function updateMenuApi(id: string, data: Partial<Menu>) {
  return put<Menu>(`/system/menus/${id}/`, data)
}

/**
 * 删除菜单
 */
export function deleteMenuApi(id: string) {
  return del(`/system/menus/${id}/`)
}

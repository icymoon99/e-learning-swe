import type { MenuItem } from './permission'

export interface UserInfo {
  id: string
  username: string
  nickname: string
  email: string
  phone: string
  avatar: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  menus?: MenuItem[]
  permissions?: string[]
}

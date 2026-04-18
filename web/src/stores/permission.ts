import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MenuItem } from '@/types/permission'
import { storage } from '@/utils/storage'

export const usePermissionStore = defineStore('permission', () => {
  const menus = ref<MenuItem[]>(storage.get<MenuItem[]>('menus') || [])
  const permissions = ref<string[]>(storage.get<string[]>('permissions') || [])

  const hasPermission = computed(() => {
    return (permission: string) => {
      if (permissions.value.includes('*')) return true
      return permissions.value.includes(permission)
    }
  })

  const sidebarMenus = computed(() => {
    return menus.value.filter(menu => !menu.hidden).sort((a, b) => a.order - b.order)
  })

  const setMenus = (menuList: MenuItem[]) => {
    menus.value = menuList
    storage.set('menus', menuList)
  }

  const setPermissions = (perms: string[]) => {
    permissions.value = perms
    storage.set('permissions', perms)
  }

  const clear = () => {
    menus.value = []
    permissions.value = []
    storage.remove('menus')
    storage.remove('permissions')
  }

  return {
    menus,
    permissions,
    hasPermission,
    sidebarMenus,
    setMenus,
    setPermissions,
    clear,
  }
})

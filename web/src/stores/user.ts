import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'
import { getUserProfileApi } from '@/api/user'
import { usePermissionStore } from './permission'
import { storage } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  // State
  const userInfo = ref<UserInfo | null>(storage.get<UserInfo>('user_info') || null)
  const isLoading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!userInfo.value)

  const isAdmin = computed(() => {
    const permissionStore = usePermissionStore()
    return permissionStore.permissions.includes('*')
  })

  const avatar = computed(() => userInfo.value?.avatar || '')
  const displayName = computed(() => userInfo.value?.nickname || userInfo.value?.username || '管理员')

  // Actions
  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    const permissionStore = usePermissionStore()
    permissionStore.setMenus(info.menus || [])
    permissionStore.setPermissions(info.permissions || [])
    storage.set('user_info', info)
  }

  const loadUserInfo = async () => {
    if (userInfo.value) {
      const permissionStore = usePermissionStore()
      permissionStore.setMenus(userInfo.value.menus || [])
      permissionStore.setPermissions(userInfo.value.permissions || [])
      return userInfo.value
    }

    const cached = storage.get<UserInfo>('user_info')
    if (cached) {
      userInfo.value = cached
      const permissionStore = usePermissionStore()
      permissionStore.setMenus(cached.menus || [])
      permissionStore.setPermissions(cached.permissions || [])
      return cached
    }

    isLoading.value = true
    try {
      const { data } = await getUserProfileApi()
      if (data.code === 0 && data.content) {
        setUserInfo(data.content)
        return data.content
      }
    } finally {
      isLoading.value = false
    }
    return null
  }

  const clearUserInfo = () => {
    userInfo.value = null
    storage.remove('user_info')
  }

  return {
    userInfo,
    isLoading,
    isLoggedIn,
    isAdmin,
    avatar,
    displayName,
    setUserInfo,
    loadUserInfo,
    clearUserInfo,
  }
})

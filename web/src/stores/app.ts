import { defineStore } from 'pinia'
import { ref } from 'vue'
import { storage } from '@/utils/storage'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(storage.get<boolean>('sidebar_collapsed') || false)
  const theme = ref<'light' | 'dark'>(storage.get<'light' | 'dark'>('theme') || 'light')
  const language = ref<'zh-CN' | 'en-US'>(storage.get<'zh-CN' | 'en-US'>('language') || 'zh-CN')
  const pageLoading = ref(false)

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    storage.set('sidebar_collapsed', sidebarCollapsed.value)
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    storage.set('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  const setLanguage = (lang: 'zh-CN' | 'en-US') => {
    language.value = lang
    storage.set('language', lang)
  }

  const setPageLoading = (loading: boolean) => {
    pageLoading.value = loading
  }

  const init = () => {
    const savedTheme = storage.get<'light' | 'dark'>('theme')
    if (savedTheme) {
      theme.value = savedTheme
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    }
  }

  return {
    sidebarCollapsed,
    theme,
    language,
    pageLoading,
    toggleSidebar,
    setTheme,
    setLanguage,
    setPageLoading,
    init,
  }
})

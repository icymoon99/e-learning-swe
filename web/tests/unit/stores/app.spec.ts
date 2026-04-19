import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAppStore } from '@/stores/app'
import { storage } from '@/utils/storage'

describe('app store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    storage.clear()
    document.documentElement.classList.remove('dark')
  })

  describe('initial state', () => {
    it('should have default values', () => {
      const store = useAppStore()
      expect(store.sidebarCollapsed).toBe(false)
      expect(store.theme).toBe('light')
      expect(store.language).toBe('zh-CN')
      expect(store.pageLoading).toBe(false)
    })

    it('should restore sidebar state from storage', () => {
      storage.set('sidebar_collapsed', true)
      const store = useAppStore()
      expect(store.sidebarCollapsed).toBe(true)
    })
  })

  describe('toggleSidebar', () => {
    it('should toggle sidebar collapsed state', () => {
      const store = useAppStore()
      store.toggleSidebar()
      expect(store.sidebarCollapsed).toBe(true)
      expect(storage.get('sidebar_collapsed')).toBe(true)

      store.toggleSidebar()
      expect(store.sidebarCollapsed).toBe(false)
    })
  })

  describe('setTheme', () => {
    it('should set theme and update storage', () => {
      const store = useAppStore()
      store.setTheme('dark')
      expect(store.theme).toBe('dark')
      expect(storage.get('theme')).toBe('dark')
    })
  })

  describe('setLanguage', () => {
    it('should set language and persist to storage', () => {
      const store = useAppStore()
      store.setLanguage('en-US')
      expect(store.language).toBe('en-US')
      expect(storage.get('language')).toBe('en-US')
    })
  })
})

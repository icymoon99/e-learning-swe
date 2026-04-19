import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { usePermissionStore } from '@/stores/permission'
import { storage } from '@/utils/storage'
import type { MenuItem } from '@/types/permission'

describe('permission store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    storage.clear()
  })

  describe('initial state', () => {
    it('should have empty menus and permissions', () => {
      const store = usePermissionStore()
      expect(store.menus).toEqual([])
      expect(store.permissions).toEqual([])
    })
  })

  describe('setMenus / setPermissions', () => {
    it('should set menus and persist to storage', () => {
      const store = usePermissionStore()
      const menus: MenuItem[] = [
        { id: '1', name: 'Dashboard', path: '/dashboard', order: 1, hidden: false },
      ]
      store.setMenus(menus)
      expect(store.menus).toEqual(menus)
      expect(storage.get('menus')).toEqual(menus)
    })

    it('should set permissions and persist to storage', () => {
      const store = usePermissionStore()
      store.setPermissions(['user:view', 'user:edit'])
      expect(store.permissions).toEqual(['user:view', 'user:edit'])
      expect(storage.get('permissions')).toEqual(['user:view', 'user:edit'])
    })
  })

  describe('hasPermission', () => {
    it('should return true for existing permission', () => {
      const store = usePermissionStore()
      store.setPermissions(['user:view', 'user:edit'])
      expect(store.hasPermission('user:view')).toBe(true)
    })

    it('should return false for non-existing permission', () => {
      const store = usePermissionStore()
      store.setPermissions(['user:view'])
      expect(store.hasPermission('system:manage')).toBe(false)
    })

    it('should return true for wildcard (*) permission', () => {
      const store = usePermissionStore()
      store.setPermissions(['*'])
      expect(store.hasPermission('anything:here')).toBe(true)
    })
  })

  describe('sidebarMenus', () => {
    it('should filter out hidden menus and sort by order', () => {
      const store = usePermissionStore()
      store.setMenus([
        { id: '1', name: 'System', path: '/system', order: 2, hidden: false },
        { id: '2', name: 'Hidden', path: '/hidden', order: 0, hidden: true },
        { id: '3', name: 'User', path: '/user', order: 1, hidden: false },
      ])
      const visible = store.sidebarMenus
      expect(visible).toHaveLength(2)
      expect(visible[0].name).toBe('User')
      expect(visible[1].name).toBe('System')
    })
  })

  describe('clear', () => {
    it('should clear menus and permissions', () => {
      const store = usePermissionStore()
      store.setMenus([{ id: '1', name: 'A', path: '/a', order: 1, hidden: false }])
      store.setPermissions(['*'])
      store.clear()
      expect(store.menus).toEqual([])
      expect(store.permissions).toEqual([])
    })
  })
})

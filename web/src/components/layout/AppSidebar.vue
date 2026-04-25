<template>
  <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon"></div>
      <span class="sidebar-logo-text" v-show="!appStore.sidebarCollapsed">SWE</span>
    </div>

    <nav class="sidebar-nav">
      <template v-for="menu in sidebarMenus" :key="menu.name">
        <div class="nav-section-label" v-show="!appStore.sidebarCollapsed">{{ menu.section }}</div>
        <template v-for="item in menu.items" :key="item.path">
          <router-link
            :to="item.path"
            class="nav-item"
            :class="{ active: isActive(item.path) }"
            :title="appStore.sidebarCollapsed ? item.title : undefined"
          >
            <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
            <span v-show="!appStore.sidebarCollapsed">{{ item.title }}</span>
          </router-link>
        </template>
      </template>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'
import { asyncRoutes } from '@/router/routes'

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

interface NavItem {
  path: string
  icon: string
  title: string
}

interface NavSection {
  section: string
  items: NavItem[]
  name: string
}

const sidebarMenus = computed<NavSection[]>(() => {
  return asyncRoutes
    .filter(r => {
      if (!r.meta?.permission) return true
      return permissionStore.permissions.includes('*') ||
        permissionStore.permissions.includes(r.meta.permission as string)
    })
    .filter(r => r.meta?.title)
    .map(r => {
      const parentPath = r.path.startsWith('/') ? r.path : `/${r.path}`
      return {
        section: (r.meta?.title as string) || '',
        name: r.name as string,
        items: (r.children || []).map(c => ({
          path: `${parentPath}/${c.path}`,
          icon: (r.meta?.icon as string) || '',
          title: (c.meta?.title as string) || (r.meta?.title as string) || '',
        })),
      }
    })
})

function isActive(path: string): boolean {
  const target = route.meta.activeMenu as string || route.path
  return target === path || target.startsWith(path + '/')
}
</script>

<style scoped lang="scss">
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  border-right: 1px solid var(--border-sidebar);
  transition: width 220ms cubic-bezier(0.4, 0, 0.2, 1);

  &.collapsed {
    width: var(--sidebar-collapsed-width);
  }
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  right: 15%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.7), transparent);
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-sidebar);
  flex-shrink: 0;
}

.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), #6366f1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.sidebar-logo-icon::after {
  content: '';
  width: 14px;
  height: 14px;
  border: 2px solid white;
  border-radius: 3px;
  transform: rotate(45deg);
}

.sidebar-logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
}

.nav-section-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 12px 12px 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  margin-bottom: 2px;

  &:hover {
    background: var(--sidebar-hover);
    color: var(--text-primary);
  }

  &.active {
    background: var(--sidebar-active);
    color: var(--primary);
    font-weight: 600;

    .nav-icon {
      color: var(--primary);
    }
  }
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
</style>

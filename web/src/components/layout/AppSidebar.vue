<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="appStore.sidebarCollapsed"
    :unique-opened="true"
    background-color="#304156"
    text-color="#bfcbd9"
    active-text-color="#409eff"
    router
  >
    <!-- 仪表盘（固定入口） -->
    <el-menu-item index="/dashboard">
      <el-icon><Odometer /></el-icon>
      <template #title>仪表盘</template>
    </el-menu-item>

    <!-- 动态菜单（根据 asyncRoutes 和权限渲染） -->
    <template v-for="menu in sidebarMenus" :key="menu.name">
      <el-sub-menu v-if="menu.children?.length" :index="menu.path">
        <template #title>
          <el-icon><component :is="menu.icon" /></el-icon>
          <span>{{ menu.title }}</span>
        </template>
        <el-menu-item
          v-for="child in menu.children"
          :key="child.name"
          :index="child.path"
        >
          {{ child.title }}
        </el-menu-item>
      </el-sub-menu>
    </template>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'
import { asyncRoutes } from '@/router/routes'
import { Odometer } from '@element-plus/icons-vue'
import type { MenuItem as MenuRoute } from '@/types/permission'

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const activeMenu = computed(() => {
  return (route.meta.activeMenu as string) || route.path
})

// 将 asyncRoutes 扁平化为菜单数据结构
interface SidebarMenu {
  name: string
  path: string
  icon: string
  title: string
  children?: { name: string; path: string; title: string }[]
}

const sidebarMenus = computed<SidebarMenu[]>(() => {
  return asyncRoutes
    .filter(r => {
      if (!r.meta?.permission) return true
      return permissionStore.permissions.includes('*') ||
        permissionStore.permissions.includes(r.meta.permission as string)
    })
    .map(r => {
      // 构建子路由的完整路径
      const parentPath = r.path.startsWith('/') ? r.path : `/${r.path}`
      const children = (r.children || []).map(c => ({
        name: c.name as string,
        path: `${parentPath}/${c.path}`,
        title: (c.meta?.title as string) || '',
      }))
      return {
        name: r.name as string,
        path: parentPath,
        icon: (r.meta?.icon as string) || '',
        title: (r.meta?.title as string) || '',
        children: children.length ? children : undefined,
      }
    })
})
</script>

<style scoped lang="scss">
.el-menu {
  border-right: none;
}
</style>

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
    <template v-for="route in sidebarRoutes" :key="route.name as string">
      <el-sub-menu v-if="route.children?.length" :index="route.name as string">
        <template #title>
          <el-icon><component :is="route.meta?.icon" /></el-icon>
          <span>{{ route.meta?.title }}</span>
        </template>
        <el-menu-item
          v-for="child in route.children"
          :key="child.name as string"
          :index="`/${route.path}/${child.path}`"
        >
          {{ child.meta?.title }}
        </el-menu-item>
      </el-sub-menu>
      <el-menu-item v-else :index="`/${route.path}`">
        <el-icon><component :is="route.meta?.icon" /></el-icon>
        <template #title>{{ route.meta?.title }}</template>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'
import { asyncRoutes } from '@/router/routes'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import { Odometer } from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const activeMenu = computed(() => {
  return (route.meta.activeMenu as string) || route.path
})

// 根据权限过滤动态路由
const sidebarRoutes = computed(() => {
  return asyncRoutes.filter(r => {
    if (!r.meta?.permission) return true
    return permissionStore.permissions.includes('*') ||
      permissionStore.permissions.includes(r.meta.permission as string)
  })
})
</script>

<style scoped lang="scss">
.el-menu {
  border-right: none;
}
</style>

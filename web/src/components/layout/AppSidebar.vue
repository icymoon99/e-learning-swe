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
    <el-menu-item index="/dashboard">
      <el-icon><Odometer /></el-icon>
      <template #title>仪表盘</template>
    </el-menu-item>

    <el-sub-menu index="user">
      <template #title>
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </template>
      <el-menu-item index="/user/list">用户列表</el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="system">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>系统管理</span>
      </template>
      <el-menu-item index="/system/menu">菜单管理</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()

const activeMenu = computed(() => {
  return (route.meta.activeMenu as string) || route.path
})
</script>

<style scoped lang="scss">
.el-menu {
  border-right: none;
}
</style>

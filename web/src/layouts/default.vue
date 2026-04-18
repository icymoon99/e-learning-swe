<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <div
      class="sidebar"
      :class="{ 'sidebar-collapsed': appStore.sidebarCollapsed }"
    >
      <div class="logo-container">
        <span v-if="!appStore.sidebarCollapsed" class="logo-text">E-Learning SWE</span>
        <span v-else class="logo-text">SWE</span>
      </div>
      <AppSidebar />
    </div>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶栏 -->
      <header class="app-header">
        <AppHeader />
      </header>

      <!-- 面包屑 -->
      <div class="app-breadcrumb">
        <AppBreadcrumb />
      </div>

      <!-- 内容区 -->
      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue'

const appStore = useAppStore()
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.app-wrapper {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: $sidebar-width;
  background-color: #304156;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;

  &.sidebar-collapsed {
    width: $sidebar-collapsed-width;
  }
}

.logo-container {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;

  .logo-text {
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    white-space: nowrap;
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-header {
  height: $header-height;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 10;
}

.app-breadcrumb {
  padding: 8px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f0f2f5;
}

// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

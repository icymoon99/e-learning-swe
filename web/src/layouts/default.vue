<template>
  <div class="app-wrapper app-bg app-grid-overlay">
    <!-- Background orbs -->
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>

    <!-- 侧边栏 -->
    <AppSidebar />

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶栏 -->
      <header class="app-header-bar">
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
  position: relative;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.app-header-bar {
  background: transparent;
}

.app-breadcrumb {
  padding: 8px 20px;
  background: transparent;
  border-bottom: 1px solid var(--border-light);
}

.app-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: transparent;
  position: relative;
  z-index: 1;
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

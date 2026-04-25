<template>
  <header class="app-header">
    <div class="header-left">
      <button class="collapse-btn" @click="toggleSidebar" aria-label="折叠侧边栏">
        <el-icon :size="20">
          <Fold v-if="!appStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </button>
      <span class="header-title">{{ route.meta.title }}</span>
    </div>
    <div class="header-right">
      <button class="header-action" @click="toggleFullscreen" aria-label="全屏">
        <el-icon :size="18"><FullScreen /></el-icon>
      </button>
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-avatar">
          {{ userStore.displayName?.charAt(0) || 'A' }}
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import { Fold, Expand, FullScreen, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

const toggleSidebar = () => appStore.toggleSidebar()

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    handleLogout()
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    authStore.logout()
    userStore.clearUserInfo()
    permissionStore.clear()
    router.push('/login')
  })
}
</script>

<style scoped lang="scss">
.app-header {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--surface-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-light);
  position: relative;
  z-index: 5;
  flex-shrink: 0;
}

.app-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  background: none;

  &:hover {
    background: var(--primary-light);
    color: var(--primary);
  }
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-action {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  background: none;

  &:hover {
    background: var(--primary-light);
    color: var(--primary);
  }
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  margin-left: 8px;
  transition: all 220ms cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px var(--primary-glow);

  &:hover {
    box-shadow: 0 4px 16px var(--primary-glow);
    transform: scale(1.05);
  }
}
</style>

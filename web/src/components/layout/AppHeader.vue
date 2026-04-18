<template>
  <div class="header-container">
    <div class="left-section">
      <el-icon class="collapse-btn" :size="20" @click="toggleSidebar">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <span class="page-title">{{ route.meta.title }}</span>
    </div>

    <div class="right-section">
      <!-- 全屏按钮 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="action-icon" :size="18" @click="toggleFullscreen">
          <FullScreen />
        </el-icon>
      </el-tooltip>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32">
            <el-icon><User /></el-icon>
          </el-avatar>
          <span class="username">{{ userStore.displayName }}</span>
          <el-icon><ArrowDown /></el-icon>
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
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

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
    ElMessage.success('已退出登录')
  })
}
</script>

<style scoped lang="scss">
.header-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;

  .left-section {
    display: flex;
    align-items: center;
    gap: 15px;

    .collapse-btn {
      cursor: pointer;
      color: #666;
      transition: color 0.3s;

      &:hover {
        color: #409eff;
      }
    }

    .page-title {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
  }

  .right-section {
    display: flex;
    align-items: center;
    gap: 20px;

    .action-icon {
      cursor: pointer;
      color: #666;
      transition: color 0.3s;

      &:hover {
        color: #409eff;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 5px 10px;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}
</style>

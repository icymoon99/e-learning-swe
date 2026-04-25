import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { useAppStore } from '@/stores/app'
import { asyncRoutes } from './routes'
import { ElMessage } from 'element-plus'

// 白名单路由 - 不需要登录
const whiteList = ['/login', '/error/401', '/error/404']

export function setupRouterGuard(router: Router) {
  // 前置守卫
  router.beforeEach(async (to) => {
    const authStore = useAuthStore()
    const userStore = useUserStore()
    const permissionStore = usePermissionStore()
    const appStore = useAppStore()

    // 设置页面标题
    document.title = to.meta.title
      ? `${to.meta.title} - E-Learning SWE 管理后台`
      : 'E-Learning SWE 管理后台'

    // 显示页面加载
    appStore.setPageLoading(true)

    // 白名单路由直接放行
    if (whiteList.includes(to.path)) {
      return true
    }

    // 检查认证状态
    if (!authStore.isAuthenticated) {
      if (authStore.refreshToken) {
        try {
          await authStore.refreshAccessToken()
        } catch {
          ElMessage.error('登录已过期，请重新登录')
          return `/login?redirect=${to.path}`
        }
      } else {
        return `/login?redirect=${to.path}`
      }
    }

    // 加载用户信息
    if (!userStore.userInfo) {
      try {
        await userStore.loadUserInfo()
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : '未知错误'
        ElMessage.error(`加载用户信息失败：${msg}`)
        authStore.logout()
        return `/login?redirect=${to.path}`
      }
    }

    // 检查菜单权限（超级管理员跳过）
    if (permissionStore.menus.length === 0 && !permissionStore.permissions.includes('*')) {
      ElMessage.error('您没有任何菜单权限')
      return '/error/401'
    }

    // 检查路由权限
    const requiredPermission = to.meta?.permission as string | undefined
    if (requiredPermission && !permissionStore.hasPermission(requiredPermission)) {
      ElMessage.error('没有权限访问该页面')
      return '/error/401'
    }

    return true
  })

  // 后置守卫
  router.afterEach(() => {
    const appStore = useAppStore()
    appStore.setPageLoading(false)
  })

  // 错误处理
  router.onError(() => {
    ElMessage.error('页面加载失败')
  })
}

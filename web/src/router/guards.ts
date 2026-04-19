import type { Router, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { useAppStore } from '@/stores/app'
import { asyncRoutes } from './routes'
import { ElMessage } from 'element-plus'

// 白名单路由 - 不需要登录
const whiteList = ['/login', '/error/401', '/error/404']

// 标记是否已添加动态路由
let hasAddedAsyncRoutes = false

function addAsyncRoutes(router: Router, permissions: string[]) {
  if (hasAddedAsyncRoutes) return

  const allowedRoutes = asyncRoutes.filter(route => {
    if (!route.meta?.permission) return true
    return permissions.includes('*') || permissions.includes(route.meta.permission as string)
  })

  allowedRoutes.forEach(route => {
    router.addRoute(route as RouteRecordRaw)
  })
  hasAddedAsyncRoutes = true
}

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
      // 尝试刷新 Token
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

    // 加载用户信息（包含菜单和权限）
    if (!userStore.userInfo) {
      try {
        await userStore.loadUserInfo()
        // 添加动态路由
        addAsyncRoutes(router, permissionStore.permissions)
        // 重新导航到目标路由（因为路由刚被添加）
        return { ...to, replace: true }
      } catch {
        authStore.logout()
        return `/login?redirect=${to.path}`
      }
    }

    // 确保动态路由已添加（处理刷新页面时 store 已有缓存但路由未注册的情况）
    if (!hasAddedAsyncRoutes && userStore.userInfo) {
      addAsyncRoutes(router, permissionStore.permissions)
      return { ...to, replace: true }
    }

    // 检查菜单权限（超级管理员跳过菜单检查）
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

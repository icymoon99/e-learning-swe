import { createRouter, createWebHistory } from 'vue-router'
import { constantRoutes } from './routes'
import { setupRouterGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes,
  scrollBehavior: () => ({ top: 0 }),
})

setupRouterGuard(router)

export default router

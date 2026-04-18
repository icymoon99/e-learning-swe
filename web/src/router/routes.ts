import type { RouteRecordRaw } from 'vue-router'

// 静态路由（始终可访问）
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', layout: 'blank' },
  },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
    ],
  },
  {
    path: '/error/401',
    name: '401',
    component: () => import('@/views/error/401.vue'),
    meta: { title: '无权限', layout: 'blank' },
  },
  {
    path: '/error/404',
    name: '404',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', layout: 'blank' },
  },
]

// 异步路由（需要权限的动态路由，后续扩展）
export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/user',
    name: 'User',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '用户管理', icon: 'User', permission: 'user:view' },
    redirect: '/user/list',
    children: [
      {
        path: 'list',
        name: 'UserList',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户列表', permission: 'user:view' },
      },
    ],
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '系统管理', icon: 'Setting', permission: 'system:view' },
    redirect: '/system/menu',
    children: [
      {
        path: 'menu',
        name: 'SystemMenu',
        component: () => import('@/views/system/menu/index.vue'),
        meta: { title: '菜单管理', permission: 'system:menu' },
      },
    ],
  },
]

export const routes = [...constantRoutes, ...asyncRoutes]

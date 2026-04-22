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
    path: '/q2',
    name: 'Q2',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '任务管理', icon: 'Timer', permission: 'q2:view' },
    redirect: '/q2/tasks',
    children: [
      {
        path: 'tasks',
        name: 'Q2Tasks',
        component: () => import('@/views/q2/tasks/index.vue'),
        meta: { title: 'Django-Q2 任务', permission: 'q2:view' },
      },
    ],
  },
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
  {
    path: '/sandbox',
    name: 'Sandbox',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '沙箱管理', icon: 'Monitor', permission: 'sandbox:view' },
    redirect: '/sandbox/instances',
    children: [
      {
        path: 'instances',
        name: 'SandboxInstances',
        component: () => import('@/views/sandbox/instances/index.vue'),
        meta: { title: '实例列表', permission: 'sandbox:view' },
      },
    ],
  },
  {
    path: '/agent',
    name: 'Agent',
    component: () => import('@/layouts/default.vue'),
    meta: { title: 'Agent管理', icon: 'Monitor', permission: 'agent:view' },
    redirect: '/agent/list',
    children: [
      {
        path: 'list',
        name: 'AgentList',
        component: () => import('@/views/agent/list/index.vue'),
        meta: { title: 'Agent列表', permission: 'agent:view' },
      },
      {
        path: 'execution',
        name: 'AgentExecution',
        component: () => import('@/views/agent/execution/index.vue'),
        meta: { title: '执行日志', permission: 'agent:view' },
      },
    ],
  },
  {
    path: '/git-source',
    name: 'GitSource',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '仓库源管理', icon: 'Connection', permission: 'git_source:view' },
    redirect: '/git-source/list',
    children: [
      {
        path: 'list',
        name: 'GitSourceList',
        component: () => import('@/views/git-source/index.vue'),
        meta: { title: '仓库源列表', permission: 'git_source:view' },
      },
    ],
  },
  {
    path: '/task',
    name: 'Task',
    component: () => import('@/layouts/default.vue'),
    meta: { title: '任务管理', icon: 'Document', permission: 'task:view' },
    redirect: '/task/list',
    children: [
      {
        path: 'list',
        name: 'TaskList',
        component: () => import('@/views/task/list.vue'),
        meta: { title: '任务列表', permission: 'task:view' },
      },
      {
        path: ':id',
        name: 'TaskDetail',
        component: () => import('@/views/task/detail.vue'),
        meta: { title: '任务详情', permission: 'task:view' },
      },
    ],
  },
]

export const routes = [...constantRoutes, ...asyncRoutes]

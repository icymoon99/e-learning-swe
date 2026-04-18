# Web 前端骨架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零搭建 E-Learning SWE 管理后台前端骨架，支持登录页和默认 Layout，AES 加密请求。

**Architecture:** Vite + Vue 3 + TypeScript 项目，Element Plus UI 组件库，Tailwind CSS 原子化样式，Pinia 状态管理，Vue Router 路由+守卫，Axios 拦截器处理 JWT + AES 加密。

**Tech Stack:** Vue 3.5, TypeScript 5, Vite 7, Tailwind CSS 4, Element Plus 2, Pinia 3, Vue Router 4/5, Axios, CryptoJS, Playwright

---

## File Map

| 文件 | 操作 | 职责 |
|------|------|------|
| `web/package.json` | Create | 项目依赖 |
| `web/vite.config.ts` | Create | Vite 配置 + API 代理 |
| `web/tsconfig.json` | Create | TypeScript 配置 |
| `web/tsconfig.app.json` | Create | App TS 配置 |
| `web/tsconfig.node.json` | Create | Node TS 配置 |
| `web/index.html` | Create | HTML 入口 |
| `web/.env.development` | Create | 开发环境变量 |
| `web/playwright.config.ts` | Create | Playwright 配置 |
| `web/src/main.ts` | Create | 入口，挂载 Element Plus + Pinia + Router |
| `web/src/App.vue` | Create | RouterView 壳，动态 Layout |
| `web/src/api/auth.ts` | Create | 登录/刷新/登出 API |
| `web/src/api/user.ts` | Create | 用户 API |
| `web/src/api/system.ts` | Create | 系统 API |
| `web/src/components/layout/AppHeader.vue` | Create | 顶栏组件 |
| `web/src/components/layout/AppSidebar.vue` | Create | 侧栏组件 |
| `web/src/components/layout/AppBreadcrumb.vue` | Create | 面包屑组件 |
| `web/src/layouts/default.vue` | Create | 默认 Layout |
| `web/src/layouts/blank.vue` | Create | 空白 Layout |
| `web/src/router/index.ts` | Create | Router 实例 |
| `web/src/router/routes.ts` | Create | 路由表 |
| `web/src/router/guards.ts` | Create | 路由守卫 |
| `web/src/stores/index.ts` | Create | Pinia 实例 |
| `web/src/stores/auth.ts` | Create | 认证 Store |
| `web/src/stores/user.ts` | Create | 用户 Store |
| `web/src/stores/app.ts` | Create | App UI Store |
| `web/src/stores/permission.ts` | Create | 权限 Store |
| `web/src/views/login/index.vue` | Create | 登录页 |
| `web/src/views/dashboard/index.vue` | Create | 仪表盘页 |
| `web/src/views/error/401.vue` | Create | 401 页 |
| `web/src/views/error/404.vue` | Create | 404 页 |
| `web/src/types/api.ts` | Create | API 类型 |
| `web/src/types/auth.ts` | Create | 认证类型 |
| `web/src/types/user.ts` | Create | 用户类型 |
| `web/src/types/permission.ts` | Create | 权限类型 |
| `web/src/types/router.ts` | Create | 路由类型 |
| `web/src/types/system.ts` | Create | 系统类型 |
| `web/src/utils/request.ts` | Create | Axios 实例 + 拦截器 |
| `web/src/utils/storage.ts` | Create | localStorage 封装 |
| `web/src/utils/aes.ts` | Create | AES 加解密 |
| `web/src/utils/format.ts` | Create | 格式化工具 |
| `web/src/utils/validate.ts` | Create | 校验工具 |
| `web/src/styles/index.scss` | Create | 全局样式 |
| `web/src/styles/variables.scss` | Create | SCSS 变量 |
| `web/tests/auth.setup.ts` | Create | E2E 认证预置 |
| `web/tests/pages/base.page.ts` | Create | Page Object 基类 |
| `web/tests/specs/login.spec.ts` | Create | 登录 E2E 测试 |

---

### Task 1: 初始化 Vite 项目

**Files:**
- Create: `web/package.json`, `web/vite.config.ts`, `web/tsconfig.json`, `web/tsconfig.app.json`, `web/tsconfig.node.json`, `web/index.html`, `web/.env.development`, `web/playwright.config.ts`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "e-learning-swe-web",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@element-plus/icons-vue": "^2.3.2",
    "axios": "^1.13.6",
    "crypto-js": "^4.2.0",
    "dayjs": "^1.11.20",
    "element-plus": "^2.13.5",
    "pinia": "^3.0.4",
    "vue": "^3.5.30",
    "vue-router": "^4.5.1"
  },
  "devDependencies": {
    "@playwright/test": "^1.58.2",
    "@types/crypto-js": "^4.2.2",
    "@types/node": "^24.12.0",
    "@vitejs/plugin-vue": "^6.0.5",
    "@vitejs/plugin-vue-jsx": "^5.1.5",
    "@vue/tsconfig": "^0.9.0",
    "prettier": "^3.8.1",
    "sass": "^1.97.3",
    "tailwindcss": "^4.1.17",
    "@tailwindcss/vite": "^4.1.17",
    "typescript": "~5.9.3",
    "vite": "^7.3.0",
    "vue-tsc": "^3.1.4"
  }
}
```

- [ ] **Step 2: 创建 vite.config.ts**

```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8600',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 创建 tsconfig.json**

```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ],
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

- [ ] **Step 4: 创建 tsconfig.app.json**

```json
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "outDir": "./dist",
    "types": ["vite/client"]
  },
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "src/**/*.vue",
    "env.d.ts"
  ],
  "exclude": ["src/**/__tests__/*", "tests/**/*"]
}
```

- [ ] **Step 5: 创建 tsconfig.node.json**

```json
{
  "extends": "@vue/tsconfig/tsconfig.node.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "allowSyntheticDefaultImports": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "./dist"
  },
  "include": ["vite.config.*"]
}
```

- [ ] **Step 6: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>E-Learning SWE 管理后台</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 7: 创建 .env.development**

```env
VITE_API_BASE_URL=/api
VITE_AES_KEY=aH5aH5bG0dC6aA3oN0cK4aU5jU6aK2lN
VITE_AES_IV=hK6eB4aE1aF3gH5q
```

- [ ] **Step 8: 创建 playwright.config.ts**

```ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/specs',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
  ],
})
```

- [ ] **Step 9: 安装依赖**

```bash
cd web && npm install
```

- [ ] **Step 10: 创建目录骨架**

```bash
mkdir -p src/{api,components/layout,layouts,router,stores,views/{login,dashboard,error,system/menu},types,utils,styles}
mkdir -p tests/{pages,specs,.auth}
mkdir -p public
```

- [ ] **Step 11: Commit**

```bash
git add web/
git commit -m "feat(web): initialize Vite project with Vue 3 + TypeScript + Element Plus + Tailwind"
```

---

### Task 2: 类型定义 + 工具函数

**Files:**
- Create: `web/src/types/api.ts`, `web/src/types/auth.ts`, `web/src/types/user.ts`, `web/src/types/permission.ts`, `web/src/types/router.ts`, `web/src/types/system.ts`
- Create: `web/src/utils/storage.ts`, `web/src/utils/aes.ts`, `web/src/utils/format.ts`, `web/src/utils/validate.ts`

- [ ] **Step 1: 创建 src/types/api.ts**

```ts
// API 通用响应格式（对应后端 ApiResponse）
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  content: T
}

// 分页响应结构
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// 分页参数
export interface PaginationParams {
  page?: number
  page_size?: number
}

// 通用列表参数
export interface ListParams extends PaginationParams {
  search?: string
  ordering?: string
}
```

- [ ] **Step 2: 创建 src/types/auth.ts**

```ts
// Token 对
export interface TokenPair {
  access: string
  refresh: string
}

// 登录凭证
export interface LoginCredentials {
  username: string
  password: string
}

// 登录响应（content 字段）
export interface LoginResponse {
  access: string
  refresh: string
}
```

- [ ] **Step 3: 创建 src/types/user.ts**

```ts
import type { MenuItem } from './permission'

export interface UserInfo {
  id: string
  username: string
  nickname: string
  email: string
  phone: string
  avatar: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  menus?: MenuItem[]
  permissions?: string[]
}
```

- [ ] **Step 4: 创建 src/types/permission.ts**

```ts
export interface MenuItem {
  id: string
  name: string
  path: string
  icon: string
  order: number
  hidden: boolean
  permission: string
  children?: MenuItem[]
}
```

- [ ] **Step 5: 创建 src/types/router.ts**

```ts
import type { RouteMeta } from 'vue-router'

export interface AppRouteMeta extends RouteMeta {
  title?: string
  icon?: string
  hidden?: boolean
  keepAlive?: boolean
  permission?: string
  activeMenu?: string
  layout?: 'default' | 'blank'
}
```

- [ ] **Step 6: 创建 src/types/system.ts**

```ts
export interface Menu {
  id: string
  name: string
  path: string
  icon: string
  order: number
  hidden: boolean
  permission: string
  parent: string | null
  created_at: string
  updated_at: string
}

export interface Group {
  id: string
  name: string
  created_at: string
  updated_at: string
}
```

- [ ] **Step 7: 创建 src/utils/storage.ts**

```ts
const PREFIX = 'el_swe_'

export const storage = {
  get<T>(key: string): T | null {
    try {
      const value = localStorage.getItem(PREFIX + key)
      if (value === null) return null
      return JSON.parse(value) as T
    } catch {
      return null
    }
  },

  set<T>(key: string, value: T): void {
    localStorage.setItem(PREFIX + key, JSON.stringify(value))
  },

  remove(key: string): void {
    localStorage.removeItem(PREFIX + key)
  },

  clear(): void {
    localStorage.clear()
  },
}
```

- [ ] **Step 8: 创建 src/utils/aes.ts**

```ts
import CryptoJS from 'crypto-js'

const AES_KEY = import.meta.env.VITE_AES_KEY || 'aH5aH5bG0dC6aA3oN0cK4aU5jU6aK2lN'
const AES_IV = import.meta.env.VITE_AES_IV || 'hK6eB4aE1aF3gH5q'

/**
 * AES 加密 (CBC 模式, PKCS7 填充)
 * 与 Django 后端解密对齐
 */
export function encryptAES(text: string): string {
  const key = CryptoJS.enc.Utf8.parse(AES_KEY)
  const iv = CryptoJS.enc.Utf8.parse(AES_IV)

  const encrypted = CryptoJS.AES.encrypt(text, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })

  return encrypted.toString()
}

/**
 * AES 解密
 */
export function decryptAES(encryptedText: string): string {
  const key = CryptoJS.enc.Utf8.parse(AES_KEY)
  const iv = CryptoJS.enc.Utf8.parse(AES_IV)

  const decrypted = CryptoJS.AES.decrypt(encryptedText, key, {
    iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7,
  })

  return decrypted.toString(CryptoJS.enc.Utf8)
}
```

- [ ] **Step 9: 创建 src/utils/format.ts**

```ts
import dayjs from 'dayjs'

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date, format = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date): string {
  return dayjs(date).format('YYYY-MM-DD')
}
```

- [ ] **Step 10: 创建 src/utils/validate.ts**

```ts
/**
 * 校验用户名
 */
export function validateUsername(username: string): boolean {
  return username.trim().length >= 2
}

/**
 * 校验密码
 */
export function validatePassword(password: string): boolean {
  return password.length >= 6
}
```

- [ ] **Step 11: Commit**

```bash
git add web/src/types/ web/src/utils/
git commit -m "feat(web): add type definitions and utility functions"
```

---

### Task 3: Axios 请求层 + API 模块

**Files:**
- Create: `web/src/utils/request.ts`
- Create: `web/src/api/auth.ts`, `web/src/api/user.ts`, `web/src/api/system.ts`

- [ ] **Step 1: 创建 src/utils/request.ts**

```ts
import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { encryptAES, decryptAES } from './aes'
import { storage } from './storage'
import type { ApiResponse } from '@/types/api'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 附加 JWT Token
    const token = storage.get<string>('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 请求体 AES 加密
    if (config.data && ['post', 'put', 'patch'].includes(config.method?.toLowerCase() || '')) {
      config.headers['Encrypted-Flag'] = 'true'
      config.data = encryptAES(JSON.stringify(config.data))
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response

    // 如果响应体是加密的，解密
    const encryptedFlag = response.headers['encrypted-flag']
    if (encryptedFlag === 'true' && typeof data === 'string') {
      return { ...response, data: JSON.parse(decryptAES(data)) }
    }

    return response
  },
  (error) => {
    const { response } = error

    if (response) {
      const { status, data } = response

      switch (status) {
        case 401:
          // Token 失效，清除并跳转登录
          storage.remove('access_token')
          storage.remove('refresh_token')
          storage.remove('token_expires_at')
          window.location.href = `/login?redirect=${window.location.pathname}`
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }

    return Promise.reject(error)
  },
)

// 便捷方法
export function get<T = unknown>(url: string, config?: AxiosRequestConfig) {
  return request.get<ApiResponse<T>>(url, config)
}

export function post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) {
  return request.post<ApiResponse<T>>(url, data, config)
}

export function put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) {
  return request.put<ApiResponse<T>>(url, data, config)
}

export function del<T = unknown>(url: string, config?: AxiosRequestConfig) {
  return request.delete<ApiResponse<T>>(url, config)
}

export default request
```

- [ ] **Step 2: 创建 src/api/auth.ts**

```ts
import { post } from '@/utils/request'
import { encryptAES } from '@/utils/aes'
import type { LoginCredentials, LoginResponse, TokenPair } from '@/types/auth'
import type { ApiResponse } from '@/types/api'

/**
 * 登录（密码 AES 加密）
 */
export function loginApi(credentials: LoginCredentials) {
  return post<LoginResponse>('/user/token/', {
    username: credentials.username,
    password: encryptAES(credentials.password),
  })
}

/**
 * 刷新 Token
 */
export function refreshTokenApi(refreshToken: string) {
  return post<TokenPair>('/user/token/refresh/', {
    refresh: refreshToken,
  })
}

/**
 * 登出
 */
export function logoutApi() {
  return post('/user/logout/')
}
```

- [ ] **Step 3: 创建 src/api/user.ts**

```ts
import { get, post, put, del } from '@/utils/request'
import type { UserInfo } from '@/types/user'
import type { ApiResponse, PaginatedResponse, ListParams } from '@/types/api'

/**
 * 获取当前用户信息
 */
export function getUserProfileApi() {
  return get<UserInfo>('/user/profile/')
}

/**
 * 获取用户列表
 */
export function getUserListApi(params?: ListParams) {
  return get<PaginatedResponse<UserInfo>>('/user/users/', { params })
}

/**
 * 获取用户详情
 */
export function getUserDetailApi(id: string) {
  return get<UserInfo>(`/user/users/${id}/`)
}

/**
 * 创建用户
 */
export function createUserApi(data: Partial<UserInfo>) {
  return post<UserInfo>('/user/users/', data)
}

/**
 * 更新用户
 */
export function updateUserApi(id: string, data: Partial<UserInfo>) {
  return put<UserInfo>(`/user/users/${id}/`, data)
}

/**
 * 删除用户
 */
export function deleteUserApi(id: string) {
  return del(`/user/users/${id}/`)
}
```

- [ ] **Step 4: 创建 src/api/system.ts**

```ts
import { get, post, put, del } from '@/utils/request'
import type { Menu } from '@/types/system'
import type { ApiResponse } from '@/types/api'

/**
 * 获取菜单列表
 */
export function getMenuListApi() {
  return get<Menu[]>('/system/menus/')
}

/**
 * 获取菜单详情
 */
export function getMenuDetailApi(id: string) {
  return get<Menu>(`/system/menus/${id}/`)
}

/**
 * 创建菜单
 */
export function createMenuApi(data: Partial<Menu>) {
  return post<Menu>('/system/menus/', data)
}

/**
 * 更新菜单
 */
export function updateMenuApi(id: string, data: Partial<Menu>) {
  return put<Menu>(`/system/menus/${id}/`, data)
}

/**
 * 删除菜单
 */
export function deleteMenuApi(id: string) {
  return del(`/system/menus/${id}/`)
}
```

- [ ] **Step 5: Commit**

```bash
git add web/src/utils/request.ts web/src/api/
git commit -m "feat(web): add Axios request layer with AES encryption and API modules"
```

---

### Task 4: Pinia Stores

**Files:**
- Create: `web/src/stores/index.ts`, `web/src/stores/auth.ts`, `web/src/stores/user.ts`, `web/src/stores/app.ts`, `web/src/stores/permission.ts`

- [ ] **Step 1: 创建 src/stores/index.ts**

```ts
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia
```

- [ ] **Step 2: 创建 src/stores/auth.ts**

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TokenPair, LoginCredentials } from '@/types/auth'
import { loginApi, refreshTokenApi } from '@/api/auth'
import { usePermissionStore } from './permission'
import { useUserStore } from './user'
import { storage } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string>(storage.get<string>('access_token') || '')
  const refreshToken = ref<string>(storage.get<string>('refresh_token') || '')
  const tokenExpiresAt = ref<number>(storage.get<number>('token_expires_at') || 0)

  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value && tokenExpiresAt.value > Date.now()
  })

  const isTokenExpiringSoon = computed(() => {
    const fiveMinutes = 5 * 60 * 1000
    return tokenExpiresAt.value - Date.now() < fiveMinutes
  })

  // Actions
  const setTokens = (tokens: TokenPair) => {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    tokenExpiresAt.value = Date.now() + 24 * 60 * 60 * 1000

    storage.set('access_token', tokens.access)
    storage.set('refresh_token', tokens.refresh)
    storage.set('token_expires_at', tokenExpiresAt.value)
  }

  const clearTokens = () => {
    accessToken.value = ''
    refreshToken.value = ''
    tokenExpiresAt.value = 0

    storage.remove('access_token')
    storage.remove('refresh_token')
    storage.remove('token_expires_at')
  }

  const login = async (credentials: LoginCredentials) => {
    const { data } = await loginApi(credentials)
    if (data.code === 0 && data.content) {
      setTokens({
        access: data.content.access,
        refresh: data.content.refresh,
      })
      return true
    }
    throw new Error(data.message || '登录失败')
  }

  const refreshAccessToken = async (): Promise<string> => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const { data } = await refreshTokenApi(refreshToken.value)
      if (data.code === 0 && data.content) {
        setTokens({
          access: data.content.access,
          refresh: data.content.refresh,
        })
        return data.content.access
      }
      throw new Error('Token refresh failed')
    } catch (error) {
      clearTokens()
      throw error
    }
  }

  const logout = () => {
    clearTokens()
    const permissionStore = usePermissionStore()
    const userStore = useUserStore()
    permissionStore.clear()
    userStore.clearUserInfo()
  }

  return {
    accessToken,
    refreshToken,
    tokenExpiresAt,
    isAuthenticated,
    isTokenExpiringSoon,
    setTokens,
    clearTokens,
    login,
    refreshAccessToken,
    logout,
  }
})
```

- [ ] **Step 3: 创建 src/stores/user.ts**

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'
import { getUserProfileApi } from '@/api/user'
import { usePermissionStore } from './permission'
import { storage } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  // State
  const userInfo = ref<UserInfo | null>(storage.get<UserInfo>('user_info') || null)
  const isLoading = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!userInfo.value)

  const isAdmin = computed(() => {
    const permissionStore = usePermissionStore()
    return permissionStore.permissions.includes('*')
  })

  const avatar = computed(() => userInfo.value?.avatar || '')
  const displayName = computed(() => userInfo.value?.nickname || userInfo.value?.username || '管理员')

  // Actions
  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    const permissionStore = usePermissionStore()
    permissionStore.setMenus(info.menus || [])
    permissionStore.setPermissions(info.permissions || [])
    storage.set('user_info', info)
  }

  const loadUserInfo = async () => {
    if (userInfo.value) {
      const permissionStore = usePermissionStore()
      permissionStore.setMenus(userInfo.value.menus || [])
      permissionStore.setPermissions(userInfo.value.permissions || [])
      return userInfo.value
    }

    const cached = storage.get<UserInfo>('user_info')
    if (cached) {
      userInfo.value = cached
      const permissionStore = usePermissionStore()
      permissionStore.setMenus(cached.menus || [])
      permissionStore.setPermissions(cached.permissions || [])
      return cached
    }

    isLoading.value = true
    try {
      const { data } = await getUserProfileApi()
      if (data.code === 0 && data.content) {
        setUserInfo(data.content)
        return data.content
      }
    } finally {
      isLoading.value = false
    }
    return null
  }

  const clearUserInfo = () => {
    userInfo.value = null
    storage.remove('user_info')
  }

  return {
    userInfo,
    isLoading,
    isLoggedIn,
    isAdmin,
    avatar,
    displayName,
    setUserInfo,
    loadUserInfo,
    clearUserInfo,
  }
})
```

- [ ] **Step 4: 创建 src/stores/app.ts**

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { storage } from '@/utils/storage'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(storage.get<boolean>('sidebar_collapsed') || false)
  const theme = ref<'light' | 'dark'>(storage.get<'light' | 'dark'>('theme') || 'light')
  const language = ref<'zh-CN' | 'en-US'>(storage.get<'zh-CN' | 'en-US'>('language') || 'zh-CN')
  const pageLoading = ref(false)

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    storage.set('sidebar_collapsed', sidebarCollapsed.value)
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    storage.set('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  const setLanguage = (lang: 'zh-CN' | 'en-US') => {
    language.value = lang
    storage.set('language', lang)
  }

  const setPageLoading = (loading: boolean) => {
    pageLoading.value = loading
  }

  const init = () => {
    const savedTheme = storage.get<'light' | 'dark'>('theme')
    if (savedTheme) {
      theme.value = savedTheme
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    }
  }

  return {
    sidebarCollapsed,
    theme,
    language,
    pageLoading,
    toggleSidebar,
    setTheme,
    setLanguage,
    setPageLoading,
    init,
  }
})
```

- [ ] **Step 5: 创建 src/stores/permission.ts**

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MenuItem } from '@/types/permission'
import type { RouteRecordRaw } from 'vue-router'
import { storage } from '@/utils/storage'

export const usePermissionStore = defineStore('permission', () => {
  const menus = ref<MenuItem[]>(storage.get<MenuItem[]>('menus') || [])
  const permissions = ref<string[]>(storage.get<string[]>('permissions') || [])
  const routes = ref<RouteRecordRaw[]>([])

  const hasPermission = computed(() => {
    return (permission: string) => {
      if (permissions.value.includes('*')) return true
      return permissions.value.includes(permission)
    }
  })

  const sidebarMenus = computed(() => {
    return menus.value.filter(menu => !menu.hidden).sort((a, b) => a.order - b.order)
  })

  const setMenus = (menuList: MenuItem[]) => {
    menus.value = menuList
    storage.set('menus', menuList)
  }

  const setPermissions = (perms: string[]) => {
    permissions.value = perms
    storage.set('permissions', perms)
  }

  const clear = () => {
    menus.value = []
    permissions.value = []
    routes.value = []
    storage.remove('menus')
    storage.remove('permissions')
  }

  return {
    menus,
    permissions,
    routes,
    hasPermission,
    sidebarMenus,
    setMenus,
    setPermissions,
    clear,
  }
})
```

- [ ] **Step 6: Commit**

```bash
git add web/src/stores/
git commit -m "feat(web): add Pinia stores (auth, user, app, permission)"
```

---

### Task 5: Router 路由 + 守卫

**Files:**
- Create: `web/src/router/index.ts`, `web/src/router/routes.ts`, `web/src/router/guards.ts`

- [ ] **Step 1: 创建 src/router/routes.ts**

```ts
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
```

- [ ] **Step 2: 创建 src/router/index.ts**

```ts
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
```

- [ ] **Step 3: 创建 src/router/guards.ts**

```ts
import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { useAppStore } from '@/stores/app'
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
      } catch {
        authStore.logout()
        return `/login?redirect=${to.path}`
      }
    }

    // 检查菜单权限
    if (permissionStore.menus.length === 0) {
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
```

- [ ] **Step 4: Commit**

```bash
git add web/src/router/
git commit -m "feat(web): add Vue Router with authentication guards"
```

---

### Task 6: Layout 布局组件

**Files:**
- Create: `web/src/layouts/default.vue`, `web/src/layouts/blank.vue`
- Create: `web/src/components/layout/AppHeader.vue`, `web/src/components/layout/AppSidebar.vue`, `web/src/components/layout/AppBreadcrumb.vue`
- Create: `web/src/styles/index.scss`, `web/src/styles/variables.scss`
- Create: `web/src/App.vue`
- Create: `web/src/main.ts`

- [ ] **Step 1: 创建 src/styles/variables.scss**

```scss
// Element Plus 主题变量覆盖
$--el-color-primary: #409eff;
$--el-menu-base-level-padding: 20px;
$--el-menu-item-height: 50px;

// 布局变量
$header-height: 56px;
$sidebar-width: 210px;
$sidebar-collapsed-width: 64px;
```

- [ ] **Step 2: 创建 src/styles/index.scss**

```scss
@use 'variables' as *;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: #333;
  background-color: #f0f2f5;
}

#app {
  height: 100%;
}

a {
  color: var(--el-color-primary);
  text-decoration: none;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background: transparent;
}
```

- [ ] **Step 3: 创建 src/App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
appStore.init()
</script>

<style>
/* 全局样式通过 main.ts 引入 */
</style>
```

- [ ] **Step 4: 创建 src/layouts/blank.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 5: 创建 src/layouts/default.vue**

```vue
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
    <div
      class="main-container"
      :class="{ 'main-expanded': appStore.sidebarCollapsed }"
    >
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
  margin-left: 0;
  transition: margin-left 0.3s;
  overflow: hidden;

  &.main-expanded {
    margin-left: 0;
  }
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
```

- [ ] **Step 6: 创建 src/components/layout/AppHeader.vue**

```vue
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
```

- [ ] **Step 7: 创建 src/components/layout/AppSidebar.vue**

```vue
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
  return route.meta.activeMenu as string || route.path
})
</script>

<style scoped lang="scss">
.el-menu {
  border-right: none;
}
</style>
```

- [ ] **Step 8: 创建 src/components/layout/AppBreadcrumb.vue**

```vue
<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
    <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
      {{ item.meta.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta?.title)
})
</script>
```

- [ ] **Step 9: 创建 src/main.ts**

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'virtual:tailwindcss'
import '@/styles/index.scss'

import App from './App.vue'
import router from './router'
import pinia from './stores'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(pinia)
app.use(router)

app.mount('#app')
```

- [ ] **Step 10: Commit**

```bash
git add web/src/main.ts web/src/App.vue web/src/layouts/ web/src/components/layout/ web/src/styles/
git commit -m "feat(web): add layout components and main entry"
```

---

### Task 7: 视图页面

**Files:**
- Create: `web/src/views/login/index.vue`, `web/src/views/dashboard/index.vue`, `web/src/views/error/401.vue`, `web/src/views/error/404.vue`
- Create placeholder views: `web/src/views/user/index.vue`, `web/src/views/system/menu/index.vue`

- [ ] **Step 1: 创建 src/views/login/index.vue**

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>E-Learning SWE</h1>
        <p>管理后台</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少 2 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  const form = formRef.value
  if (!form) return

  await form.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await authStore.login(loginForm)
      ElMessage.success('登录成功')
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } catch (error: any) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;

  h1 {
    font-size: 28px;
    color: #333;
    margin-bottom: 8px;
  }

  p {
    color: #999;
    font-size: 14px;
  }
}

.login-form {
  .login-btn {
    width: 100%;
  }
}
</style>
```

- [ ] **Step 2: 创建 src/views/dashboard/index.vue**

```vue
<template>
  <div class="dashboard-container">
    <h2 class="page-title">仪表盘</h2>
    <el-row :gutter="20" class="mt-6">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#409eff"><User /></el-icon>
              <span class="ml-2">用户数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#67c23a"><Document /></el-icon>
              <span class="ml-2">任务数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon :size="24" color="#e6a23c"><Folder /></el-icon>
              <span class="ml-2">仓库数</span>
            </div>
          </template>
          <div class="card-value">--</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { User, Document, Folder } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  text-align: center;
  padding: 16px 0;
}
</style>
```

- [ ] **Step 3: 创建 src/views/error/401.vue**

```vue
<template>
  <div class="error-container">
    <div class="error-content">
      <h1 class="error-code">401</h1>
      <p class="error-msg">您没有访问权限，请联系管理员</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.error-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.error-content {
  text-align: center;

  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: #409eff;
    margin-bottom: 16px;
  }

  .error-msg {
    font-size: 18px;
    color: #999;
    margin-bottom: 32px;
  }
}
</style>
```

- [ ] **Step 4: 创建 src/views/error/404.vue**

```vue
<template>
  <div class="error-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <p class="error-msg">页面不存在，请检查网址</p>
      <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.error-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.error-content {
  text-align: center;

  .error-code {
    font-size: 120px;
    font-weight: 700;
    color: #409eff;
    margin-bottom: 16px;
  }

  .error-msg {
    font-size: 18px;
    color: #999;
    margin-bottom: 32px;
  }
}
</style>
```

- [ ] **Step 5: 创建 src/views/user/index.vue（占位）**

```vue
<template>
  <div>
    <h2>用户管理</h2>
    <p class="text-gray-500 mt-4">功能开发中...</p>
  </div>
</template>
```

- [ ] **Step 6: 创建 src/views/system/menu/index.vue（占位）**

```vue
<template>
  <div>
    <h2>菜单管理</h2>
    <p class="text-gray-500 mt-4">功能开发中...</p>
  </div>
</template>
```

- [ ] **Step 7: Commit**

```bash
git add web/src/views/
git commit -m "feat(web): add login, dashboard, error pages and placeholder views"
```

---

### Task 8: E2E 测试骨架 + 验证

**Files:**
- Create: `web/tests/auth.setup.ts`, `web/tests/pages/base.page.ts`, `web/tests/specs/login.spec.ts`

- [ ] **Step 1: 创建 tests/auth.setup.ts**

```ts
import { test as setup } from '@playwright/test'
import path from 'path'

const authFile = path.join(__dirname, '../.auth/user.json')

setup('authenticate as admin', async ({ page }) => {
  await page.goto('/login')
  await page.getByPlaceholder('用户名').fill('admin')
  await page.getByPlaceholder('密码').fill('Admin@1234')
  await page.getByRole('button', { name: '登 录' }).click()
  await page.waitForURL('/')
  await page.context().storageState({ path: authFile })
})
```

- [ ] **Step 2: 创建 tests/pages/base.page.ts**

```ts
import type { Page, Locator } from '@playwright/test'

export class BasePage {
  readonly page: Page
  readonly sidebar: Locator
  readonly header: Locator

  constructor(page: Page) {
    this.page = page
    this.sidebar = page.locator('.sidebar')
    this.header = page.locator('.app-header')
  }

  async navigateTo(path: string) {
    await this.page.goto(path)
  }

  async clickSidebarItem(text: string) {
    await this.page.getByText(text).click()
  }
}
```

- [ ] **Step 3: 创建 tests/specs/login.spec.ts**

```ts
import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('should show login form', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByPlaceholder('用户名')).toBeVisible()
    await expect(page.getByPlaceholder('密码')).toBeVisible()
    await expect(page.getByRole('button', { name: '登 录' })).toBeVisible()
  })

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: '登 录' }).click()
    await expect(page.getByText('请输入用户名')).toBeVisible()
    await expect(page.getByText('请输入密码')).toBeVisible()
  })

  test('should redirect to dashboard on successful login', async ({ page }) => {
    await page.goto('/login')
    await page.getByPlaceholder('用户名').fill('admin')
    await page.getByPlaceholder('密码').fill('Admin@1234')
    await page.getByRole('button', { name: '登 录' }).click()
    await page.waitForURL('/')
    await expect(page).toHaveURL('/')
  })
})
```

- [ ] **Step 4: 运行 Django check 验证后端可用**

```bash
cd /Users/willie/e-learning/e-learning-swe
uv run python manage.py check
```

- [ ] **Step 5: Commit**

```bash
git add web/tests/
git commit -m "feat(web): add Playwright E2E test skeleton"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ Vite 项目初始化 → Task 1
- ✅ 安装依赖 → Task 1 (package.json + npm install)
- ✅ 目录结构 → Task 1
- ✅ vite.config.ts (proxy :8600) → Task 1
- ✅ main.ts (Element Plus + Pinia + Router) → Task 6
- ✅ router/ (路由表 + 守卫) → Task 5
- ✅ stores/auth.ts → Task 4
- ✅ utils/request.ts (Axios 拦截器 + JWT + AES) → Task 3
- ✅ utils/aes.ts (AES 加解密) → Task 2
- ✅ utils/storage.ts (localStorage token 管理) → Task 2
- ✅ layouts/default.vue + blank.vue → Task 6
- ✅ components/layout/ (Header + Sidebar + Breadcrumb) → Task 6
- ✅ views/login/index.vue (登录表单 + AES 加密) → Task 7
- ✅ API 代理到 :8600 → Task 1 (vite.config.ts)
- ✅ E2E 测试骨架 → Task 8
- ✅ TypeScript 类型定义 → Task 2
- ✅ Pinia stores (auth, user, app, permission) → Task 4
- ✅ API 模块 (auth, user, system) → Task 3
- ✅ 全局样式 + SCSS 变量 → Task 6
- ✅ 错误页 (401, 404) → Task 7
- ✅ 仪表盘页 → Task 7
- ✅ 占位页面 (user, system/menu) → Task 7

**2. Placeholder scan:** No TBD/TODO/fill-in sections found.

**3. Type consistency:** All types defined in Task 2 are used consistently in Tasks 3-7. `ApiResponse`, `TokenPair`, `LoginCredentials`, `UserInfo`, `MenuItem` all match between types, stores, and API modules.

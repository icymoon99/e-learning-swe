# Web 前端设计文档

**日期**: 2026-04-18
**项目**: E-Learning SWE 管理后台前端
**状态**: 已确认

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5+ | 前端框架 |
| TypeScript | 5 | 类型安全 |
| Vite | 7 | 构建工具 |
| Tailwind CSS | 4 | 原子化 CSS |
| Element Plus | 2 | UI 组件库 |
| Pinia | 3 | 状态管理 |
| Vue Router | 4/5 | 路由 |
| Axios | 最新 | HTTP 请求 |
| CryptoJS | 最新 | AES 加密 |
| Playwright | 最新 | E2E 测试 |

## 项目结构

```
web/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── playwright.config.ts
├── public/
│   ├── favicon.svg
│   └── icons.svg
└── src/
    ├── main.ts
    ├── App.vue
    ├── api/
    │   ├── auth.ts
    │   ├── user.ts
    │   └── system.ts
    ├── components/layout/
    │   ├── AppHeader.vue
    │   ├── AppSidebar.vue
    │   └── AppBreadcrumb.vue
    ├── layouts/
    │   ├── default.vue
    │   └── blank.vue
    ├── router/
    │   ├── index.ts
    │   ├── routes.ts
    │   └── guards.ts
    ├── stores/
    │   ├── index.ts
    │   ├── auth.ts
    │   ├── user.ts
    │   ├── app.ts
    │   └── permission.ts
    ├── views/
    │   ├── login/index.vue
    │   ├── dashboard/index.vue
    │   ├── error/
    │   │   ├── 401.vue
    │   │   └── 404.vue
    │   ├── user/index.vue
    │   └── system/menu/index.vue
    ├── types/
    │   ├── api.ts
    │   ├── auth.ts
    │   ├── user.ts
    │   └── system.ts
    ├── utils/
    │   ├── request.ts
    │   ├── storage.ts
    │   ├── format.ts
    │   ├── validate.ts
    │   └── aes.ts
    ├── styles/
    │   ├── index.scss
    │   └── variables.scss
    └── tests/
        ├── auth.setup.ts
        ├── pages/
        └── specs/
```

## 页面与路由

| 路由 | 页面 | Layout | 说明 |
|------|------|--------|------|
| `/login` | 登录页 | blank | 用户名/密码，AES 加密传输 |
| `/` | - | default | 重定向 `/dashboard` |
| `/dashboard` | 仪表盘 | default | 数据统计概览 |
| `/user` | 用户管理 | default | 用户列表 CRUD |
| `/system/menu` | 菜单管理 | default | 菜单树 CRUD |
| `/error/401` | 401 | blank | 未授权 |
| `/error/404` | 404 | blank | 未找到 |

## 架构设计

### API 层

- `utils/request.ts` 创建 Axios 实例，baseURL 通过 Vite proxy 代理到 `http://localhost:8600`
- 请求拦截器：
  - 自动附加 `Authorization: Bearer <token>`
  - 请求体通过 AES 加密（`utils/aes.ts`）
  - 附加 `Encrypted-Flag: true` 请求头
- 响应拦截器：
  - 解密响应体（如加密）
  - 401 时清除 token 并跳转登录
  - 其他错误通过 `ElMessage.error()` 提示

### AES 加密

- 密钥 `AES_KEY` 和 IV `AES_IV` 来自环境变量（Vite `env` 配置）
- `utils/aes.ts` 提供 `encrypt()` / `decrypt()` 方法
- 请求时加密，响应时解密

### 状态管理 (Pinia)

- `stores/auth.ts` — 登录状态、token 存取、登录/登出 action
- `stores/user.ts` — 当前用户信息
- `stores/app.ts` — 侧边栏折叠、主题等 UI 状态
- `stores/permission.ts` — 路由权限、动态菜单

### 路由守卫

- `router/guards.ts` 实现 beforeEach 守卫：
  - 白名单路由（`/login`, `/error/*`）直接放行
  - 无 token → 重定向 `/login`
  - 有 token 但无用户信息 → 拉取用户信息 + 动态路由
  - 已登录访问 `/login` → 重定向 `/`

### Layout

- `layouts/default.vue` — 顶栏 (AppHeader) + 侧栏 (AppSidebar) + 内容区 + 面包屑 (AppBreadcrumb)
- `layouts/blank.vue` — 仅 `<router-view />`，用于登录页和错误页
- 路由通过 `meta.layout` 字段决定使用哪个 layout

## 首期范围

本期仅搭建骨架：

1. Vite 项目初始化（`npm create vite`）
2. 安装依赖：vue-router, pinia, element-plus, tailwindcss, axios, crypto-js, sass
3. 创建上述目录结构（空文件）
4. 实现核心基础设施：
   - `vite.config.ts`（proxy 到 :8600）
   - `main.ts`（挂载 Element Plus + Pinia + Router）
   - `router/`（路由表 + 守卫）
   - `stores/auth.ts`
   - `utils/request.ts`（Axios 拦截器）
   - `utils/aes.ts`（AES 加解密）
   - `utils/storage.ts`（localStorage token 管理）
   - `layouts/default.vue` + `blank.vue`
   - `components/layout/`（Header + Sidebar + Breadcrumb 空壳）
   - `views/login/index.vue`（登录表单，暂不对接后端）
5. `dev` 模式可运行，访问 `/login` 和 `/dashboard` 页面（静态）

## 开发流程

```bash
cd web
npm install
npm run dev          # 开发服务器 :3000，API 代理 :8600
npm run build        # vue-tsc + vite build
npm run preview      # 预览构建产物
```

## 后续扩展

- 用户管理、菜单管理页面
- E2E 测试（Playwright）
- 仪表盘数据可视化
- 更多业务模块

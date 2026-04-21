# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

E-Learning SWE 教育平台后端，Django + DRF 提供 RESTful API。

| 部分 | 技术栈                             | 路径   | 说明                                              |
| ---- | ---------------------------------- | ------ | ------------------------------------------------- |
| 后端 | Django 5.2 + DRF                   | 根目录 | RESTful API，JWT 认证，Django-Q 异步任务          |
| 前端 | Vue 3.5 + TS + Vite + Element Plus | `web/` | SPA 管理后台，Pinia 状态管理，Vue Router 动态路由 |

## 常用命令

### 后端 (Django)

**项目使用 `uv` 管理 Python 虚拟环境，位于根目录 `.venv`。在非交互式 shell（脚本、后台任务、&& 链）中，必须使用 `.venv/bin/python` 直接调用，不依赖 `source activate`。**

```bash
# 安装依赖
uv pip install -r requirements.txt

# 启动开发服务器
.venv/bin/python manage.py runserver 0.0.0.0:8600

# 数据库迁移
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate

# 运行测试
.venv/bin/python manage.py test

# 系统检查
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run   # 检查是否漏迁移

# 创建超级用户
.venv/bin/python manage.py createsuperuser

# 启动 Django-Q Worker
.venv/bin/python manage.py qcluster

# 收集静态文件
.venv/bin/python manage.py collectstatic --noinput
```

### 前端 (Vue)

**所有 npm 操作必须在 `web/` 目录下执行。命令示例：`bash -c 'cd web && npm run build'`。**

```bash
# 安装依赖
cd web && npm install

# 启动开发服务器
cd web && npm run dev        # 默认 http://localhost:3001

# 类型检查 + 构建
cd web && npm run build      # vue-tsc + vite build

# 预览构建产物
cd web && npm run preview
```

## 后端架构

### 项目结构

```
e-learning-swe/
├── core/                    # Django 项目配置
│   ├── settings.py          # 项目设置
│   ├── urls.py              # 全局路由
│   └── common/              # 核心公共包
│       ├── exception/       # 统一异常响应体系 (ApiResponse / ApiException)
│       ├── ulid/            # ULID 序列化与渲染
│       └── utils/           # 通用工具 (AES 加密等)
├── user/                    # 用户管理 (自定义 ElUser 模型 + JWT 认证)
└── system/                  # 系统管理 (RBAC + 菜单)
```

### 关键架构决策

- **认证**: JWT (SimpleJWT)，Access Token 1天 / Refresh Token 7天，启用轮换与黑名单
- **权限**: 默认 `IsAuthenticated`，管理员操作使用自定义 `IsAdminUser`（`is_superuser` 校验）
- **自定义用户模型**: `user.ElUser`，自定义认证后端 `user.services.auth.ElUserAuthBackend`
- **统一响应**: 业务接口通过 `ApiResponse` 返回，异常通过 `ApiException` 抛出，由 `ExceptionGlobalMiddleware` 统一转换
- **主键**: 使用 ULID，通过 `ULIDJSONRenderer` 序列化为字符串
- **分页**: 默认 `StandardPagination`（返回 `ApiResponse` 统一格式 `{code, message, content: {count, next, previous, results}}`），每页 10 条，最大 100
- **精确过滤**: 使用 `django-filters`，在 `filters.py` 中定义 `FilterSet`，禁止直接使用 `filterset_fields`
- **模糊搜索**: 使用 `SearchFilter` 及 `search_fields`
- **结果排序**: 使用 `OrderingFilter` 及 `ordering_fields`
- **异步任务**: Django-Q，通过 Redis + ORM 作为 broker
- **数据库**: 默认 SQLite3，可通过 `DB_ENGINE=mysql` 切换 MySQL
- **API 文档**: drf-spectacular，自动生成 OpenAPI schema (`/api/schema/`)

### 每个业务 app 的标准结构

```
app_name/
├── models.py        # 数据模型 (继承 AbstractBaseModel)
├── serializers.py   # DRF 序列化器
├── filters.py       # django-filters FilterSet
├── urls.py          # 路由
├── views/
│   ├── __init__.py  # 导出视图
│   └── *_view.py    # 视图逻辑
├── services/        # (可选) 业务逻辑服务层
├── admin.py         # Django Admin 配置
├── tests/           # 测试目录
│   └── *_test.py    # 功能测试文件
```

## 前端架构

### 项目结构

```
e-learning-swe/web/
├── src/
│   ├── api/              # API 请求封装（按业务模块分组）
│   ├── components/       # 业务组件
│   │   └── layout/       # 布局组件（AppSidebar 等）
│   ├── router/           # 路由配置
│   │   ├── index.ts      # 路由器创建（注册全部路由）
│   │   ├── routes.ts     # 路由定义（constantRoutes + asyncRoutes）
│   │   └── guards.ts     # 路由守卫（认证 + 权限检查）
│   ├── stores/           # Pinia 状态管理
│   │   ├── auth.ts       # 认证（token 管理、登录/登出）
│   │   ├── user.ts       # 用户信息
│   │   ├── permission.ts # 权限与菜单
│   │   └── app.ts        # 应用全局状态
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数（request.ts、storage.ts、aes.ts）
│   ├── views/            # 页面视图（按业务模块分组）
│   └── main.ts           # 应用入口
├── tests/
│   ├── fixtures/         # Playwright fixtures（auth.ts 认证）
│   ├── pages/            # Page Object Model
│   ├── specs/            # E2E 测试
│   └── unit/             # 单元测试
├── playwright.config.ts  # Playwright 配置
└── vite.config.ts        # Vite 配置
```

### 关键技术点

- **动态路由**: `router/index.ts` 创建时注册全部路由（含 `asyncRoutes`），路由守卫只负责权限检查
- **认证存储**: `el_swe_access_token` / `el_swe_refresh_token` / `el_swe_token_expires_at`（localStorage，前缀 `el_swe_`）
- **请求拦截**: `utils/request.ts` 自动附加 JWT Token，登录接口密码通过 AES 加密（CBC + PKCS7）
- **侧边栏菜单**: 从 `asyncRoutes` 动态渲染，根据 `permissionStore.permissions` 过滤
- **权限检查**: 超级管理员（权限 `*`）跳过菜单和路由权限检查
- **API 代理**: Vite 开发服务器将 `/api` 代理到 `http://localhost:8600`
- **测试**: Playwright E2E 使用 `context.addInitScript()` 注入 localStorage token，避免 `storageState` 与 SPA 冲突

## 开发规范

### 通用

- 所有代码和文档使用中文，符合项目需求
- 遵循项目 rules: `.claude/rules/`
- 提交信息格式: `<type>: <description>` (feat/fix/refactor/docs/test/chore)

### Vue 开发

- 组件使用 `<script setup lang="ts">`，优先 Composition API
- 使用本地扩展库 `web/src/common/extensions/` 提供的扩展方法构建页面 UI
- API 请求通过 `utils/request.ts` 封装，返回 `ApiResponse` 格式
- 状态管理使用 Pinia store，避免组件内直接操作 localStorage
- 路由新增：先在 `router/routes.ts` 的 `asyncRoutes` 中添加，侧边栏自动渲染
- npm 命令必须在 `web/` 目录下执行（`bash -c 'cd web && npm run ...'`）

### Django 开发

- 模型继承 `AbstractBaseModel`，模型名以 `El` 开头
- 视图使用 `ViewSet`，继承 `ModelViewSet` 或 `ReadOnlyModelViewSet`，通过 `@action` 扩展非标准接口
- 时间格式: `"%Y-%m-%d %H:%M:%S"`，日期格式: `"%Y-%m-%d"`
- 敏感配置必须来自环境变量
- 详细规范见 `.claude/rules/django/` 目录

### 文档规范

- **架构文档**: `docs/arch/`，命名格式 `YYYY-MM-DD-*-arch.md`
- **规格文档**: `docs/spec/`，命名格式 `YYYY-MM-DD-*-spec.md`
- **计划文档**: `docs/plan/`，命名格式 `YYYY-MM-DD-*-plan.md`
- **TDD 文档**: `docs/tdd/`，命名格式 `YYYY-MM-DD-*-tdd.md`
- **API 文档**: `docs/api/`，命名格式 `*-api.md`

⚠️ **_新增、修改、删除 `docs/` 下文档时，遵循 obsidian 的 `defuddle`、`json-canvas`、`obsidian-bases`、`obsidian-cli` 和 `obsidian-markdown` 的 skill 来操作，同步到 obsidian 的 `99_CodeDocs/e-learning-swe/*/` 下，并且和 `docs/*/` 保持一致。_**

### 完成开发后必做检查

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
```

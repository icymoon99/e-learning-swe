# E-Learning SWE

> 基于 LangGraph Agent 的智能软件工程平台 — 用 AI 完成代码分析、重构、PR 生成

[🇬🇧 English README](README.md)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 简介

E-Learning SWE 是一个 AI 驱动的软件工程平台，基于 **LangGraph Agent** 架构，提供从仓库接入、智能分析到自动 PR 生成的完整工作流。支持 GitHub、Gitee、GitLab 多平台接入，通过可视化任务管理界面下达 AI 指令，让智能体在沙箱环境中完成代码工作。

**核心能力：**

- **AI Agent 编排** — 基于 LangGraph StateGraph 构建可编排、可扩展的 Agent 执行链路
- **多平台仓库接入** — 统一抽象 GitHub/Gitee/GitLab，一键接入仓库源
- **沙箱隔离执行** — 支持本地/远程 Docker 及系统级沙箱，保障执行安全
- **任务对话流** — 类 Chat 交互界面，实时查看 Agent 执行进度与结果
- **自动 PR 生成** — Agent 完成工作后自动提交代码、创建 Pull Request
- **Django-Q2 异步队列** — 长时间任务后台执行，不阻塞前端交互

## 技术栈

### 后端

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | Django + DRF | 5.2 / 3.16 |
| Agent 引擎 | LangGraph + DeepAgent | 1.1.3 / 0.4.12 |
| LLM 接入 | langchain-openai, langchain-anthropic, dashscope | — |
| 异步任务 | Django-Q2 | 1.8.0 |
| 认证鉴权 | SimpleJWT + RBAC | 5.5.0 |
| API 文档 | drf-spectacular (OpenAPI 3.0) | 0.29.0 |
| 数据库 | SQLite3 (默认) / MySQL | — |

### 前端

| 组件 | 技术 |
|------|------|
| 框架 | Vue 3.5 + TypeScript |
| 构建 | Vite 7 + vue-tsc |
| UI | Element Plus 2.13 + Tailwind CSS 4 |
| 状态 | Pinia 3 |
| 路由 | Vue Router 4 (动态路由) |
| E2E 测试 | Playwright |

## 项目结构

```
e-learning-swe/
├── core/                     # Django 项目配置 & 公共能力
│   ├── settings.py           # 全局配置
│   ├── urls.py               # 路由入口
│   └── common/               # 公共包（异常体系、ULID、工具类）
├── agent/                    # Agent 管理 + 执行编排
│   ├── models.py             # ElAgent + ElAgentExecutionLog
│   ├── orchestrator.py       # LangGraph Agent 编排器（全局单例）
│   ├── context.py            # GitContext 数据类
│   ├── services/             # 沙箱解析器、Git 平台抽象
│   └── views/                # Agent CRUD + 执行日志 API
├── git_source/               # 仓库源管理
│   ├── models.py             # ElGitSource (GitHub/Gitee/GitLab)
│   └── views/                # 仓库源 CRUD + 下拉接口
├── task/                     # 任务管理 + 对话流
│   ├── models.py             # ElTask + ElTaskConversation
│   ├── tasks.py              # Django-Q2 异步任务函数
│   └── views/                # 任务 CRUD + 嵌套对话 API
├── sandbox/                  # 沙箱实例管理
│   └── models.py             # ElSandboxInstance
├── user/                     # 用户管理 + 自定义认证
├── system/                   # 系统管理（RBAC + 菜单）
├── q2/                       # Django-Q2 任务监控
├── web/                      # Vue 3 前端 SPA
│   ├── src/api/              # API 请求封装
│   ├── src/views/            # 页面视图
│   ├── src/router/           # 动态路由配置
│   └── src/stores/           # Pinia 状态管理
└── docs/                     # 架构/规格/计划/TDD 文档
```

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 20+
- uv（Python 包管理）
- Redis（Django-Q2 后台）

### 后端

```bash
# 1. 安装依赖（uv 管理虚拟环境）
uv pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env   # 按需编辑 .env

# 3. 数据库迁移
.venv/bin/python manage.py migrate

# 4. 创建超级用户
.venv/bin/python manage.py createsuperuser

# 5. 启动开发服务器
.venv/bin/python manage.py runserver 0.0.0.0:8600

# 6. 启动 Django-Q2 Worker（异步任务处理）
.venv/bin/python manage.py qcluster
```

### 前端

```bash
cd web

# 1. 安装依赖
npm install

# 2. 启动开发服务器（自动代理 /api 到后端）
npm run dev          # http://localhost:3001

# 3. 生产构建
npm run build        # vue-tsc + vite build
```

### 验证安装

```bash
# 后端健康检查
.venv/bin/python manage.py check

# 运行测试
.venv/bin/python manage.py test

# 前端类型检查
cd web && npm run build
```

## 功能模块

### 仓库源管理

管理 Git 仓库接入配置，支持多平台（GitHub/Gitee/GitLab）统一抽象：

- 添加/编辑/删除仓库源
- Token 自动掩码保护，详情接口不返回敏感凭证
- 下拉接口供任务创建时快速选择仓库源
- 远程仓库查询与分支选择（通过平台 API 获取）

### Agent 管理

配置 AI Agent 实例，支持多模型切换和系统提示词定制：

- Agent 增删改查（编码、名称、描述、系统提示词、模型选择）
- Agent 执行日志查看（状态、事件流、执行结果、错误信息）
- PR 结果展示（PR 地址、Commit Hash）

### 任务管理

AI 任务的核心工作区，以对话流方式与 Agent 交互：

- 创建任务：绑定仓库源和目标分支
- 发送指令：选择 Agent，输入具体任务要求
- 实时对话：用户指令 → Agent 执行 → AI 回复的完整链路
- 执行状态：running / completed / failed 可视化展示
- 任务关闭：标记任务完成并记录系统通知

### 沙箱管理

管理代码执行环境实例，支持多种隔离策略：

- 本地 Docker / 远程 Docker / 本地系统 / 远程系统
- 实例状态监控（活跃 / 未激活 / 错误）
- 配置元信息存储

### Django-Q2 监控

查看异步任务队列状态、失败任务重试、任务历史记录。

## API 文档

启动后端后访问：

- **Swagger UI**: http://localhost:8600/api/docs/
- **ReDoc**: http://localhost:8600/api/redoc/
- **OpenAPI Schema**: http://localhost:8600/api/schema/

### 主要接口

| 模块 | 接口前缀 | 说明 |
|------|----------|------|
| 用户 | `/api/user/` | 登录、Token 刷新 |
| 系统 | `/api/system/` | 菜单、角色、分组 |
| Agent | `/api/agent/` | Agent CRUD、执行日志 |
| 仓库源 | `/api/git-source/` | 仓库源 CRUD、下拉 |
| 任务 | `/api/task/` | 任务 CRUD、对话流、关闭 |
| 沙箱 | `/api/sandbox/` | 沙箱实例管理 |
| Django-Q2 | `/api/q2/` | 任务队列监控 |

### 统一响应格式

```json
{
  "code": 0,
  "message": "OK",
  "content": {
    "count": 10,
    "next": "...",
    "previous": "...",
    "results": []
  }
}
```

## 测试

```bash
# 运行全部测试
.venv/bin/python manage.py test

# 运行指定模块测试
.venv/bin/python manage.py test task git_source -v 2

# E2E 测试
cd web && npx playwright test
```

## 贡献

欢迎提交 Issue 和 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到远程 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## License

本项目基于 MIT 协议开源。

# Django-Q2 任务管理页面 — 规格文档

> **目标：** 在 Web 管理后台中创建 Django-Q2 异步任务的完整管理页面，提供运行中任务查看、失败任务重试、定时任务 CRUD、队列管理等能力。
> **范围：** 后端 API + 前端页面
> **技术栈：** Django + DRF（后端），Vue 3 + Element Plus（前端）

---

## 1. 背景

Django-Q2 不提供任何 REST API 端点，仅有 Django Admin 管理界面。当前管理后台无法查看和管理异步任务，需要自行开发 API 和前端页面。

**Django-Q2 数据模型：**

| 模型 | 用途 | 关键字段 |
|------|------|---------|
| `Task` | 已完成任务（成功/失败） | id, name, func, args, kwargs, result, started, stopped, success, attempt_count |
| `Schedule` | 定时/周期任务 | id, name, func, schedule_type, minutes, repeats, next_run, cron |
| `Failure` | 失败任务（Task 的子集视图） | 同 Task |
| `OrmQ` | ORM 队列（待执行任务） | id, key, payload, lock |

**已有能力（无需开发）：**
- Django Admin 后台管理界面
- `python manage.py qcluster` 启动 Worker
- `python manage.py qmonitor` 终端监控

**需要开发：**
- REST API 接口（10 个）
- 前端管理页面（5 个 Tab）

---

## 2. API 设计

### 2.1 任务列表

**请求：** `GET /api/q2/tasks/`

**参数：**
- `status`: `running` | `success` | `failure`（必填）
- `page`: 页码（默认 1）
- `page_size`: 每页条数（默认 20，最大 100）
- `search`: 任务名模糊搜索

**响应：**
```json
{
  "code": 0,
  "message": "ok",
  "content": {
    "count": 1247,
    "results": [
      {
        "id": "01KPG...",
        "name": "send_email_notification",
        "func": "myapp.tasks.send_email",
        "started": "2026-04-18 22:35:12",
        "stopped": null,
        "success": null,
        "result": null,
        "attempt_count": 1
      }
    ]
  }
}
```

### 2.2 任务详情

**请求：** `GET /api/q2/tasks/:id/`

**响应：** 单条任务完整信息，包含 `args`、`kwargs`、`hook`、`result`（JSON 解析后返回）。

### 2.3 删除任务

**请求：** `DELETE /api/q2/tasks/:id/`

**响应：** `{"code": 0, "message": "ok", "content": null}`

### 2.4 重试失败任务

**请求：** `POST /api/q2/failures/:id/retry/`

**逻辑：** 读取 Failure 记录，使用 `async_task()` 重新提交任务，成功后删除 Failure 记录。

**响应：**
```json
{
  "code": 0,
  "message": "ok",
  "content": {
    "task_id": "01KPH...",
    "name": "send_email_notification"
  }
}
```

### 2.5 定时任务列表

**请求：** `GET /api/q2/schedules/`

**参数：**
- `page`、`page_size`、`search`（同任务列表）

**响应：**
```json
{
  "code": 0,
  "message": "ok",
  "content": {
    "count": 5,
    "results": [
      {
        "id": 12,
        "name": "daily_report",
        "func": "myapp.tasks.daily_report",
        "schedule_type": "HOURLY",
        "minutes": null,
        "repeats": -1,
        "next_run": "2026-04-18 23:00:00",
        "cron": null,
        "task": "task_001"
      }
    ]
  }
}
```

### 2.6 创建定时任务

**请求：** `POST /api/q2/schedules/`

**请求体：**
```json
{
  "name": "weekly_cleanup",
  "func": "myapp.tasks.weekly_cleanup",
  "schedule_type": "DAILY",
  "minutes": null,
  "repeats": -1,
  "args": [],
  "kwargs": {}
}
```

**schedule_type 可选值：**
- `ONCE` — 一次性
- `MINUTES` — 按分钟间隔（需设置 `minutes` 字段）
- `HOURLY` — 每小时
- `DAILY` — 每天
- `WEEKLY` — 每周
- `MONTHLY` — 每月
- `QUARTERLY` — 每季度
- `YEARLY` — 每年
- `CRON` — Cron 表达式（需设置 `cron` 字段）

### 2.7 更新定时任务

**请求：** `PUT /api/q2/schedules/:id/`

**逻辑：** 允许修改 `name`、`schedule_type`、`minutes`、`repeats`、`args`、`kwargs`。

### 2.8 删除定时任务

**请求：** `DELETE /api/q2/schedules/:id/`

### 2.9 暂停/恢复队列

**请求：** `POST /api/q2/queue/pause/`

**请求体：** `{"action": "pause"}` 或 `{"action": "resume"}`

### 2.10 队列状态

**请求：** `GET /api/q2/queue/status/`

**响应：**
```json
{
  "code": 0,
  "message": "ok",
  "content": {
    "worker_running": true,
    "queue_size": 8,
    "tasks_running": 3,
    "tasks_failed": 12
  }
}
```

---

## 3. 前端页面设计

### 3.1 路由

`/q2/tasks` — 任务管理主页面

### 3.2 页面布局

```
┌─────────────────────────────────────────────────────┐
│  Django-Q2 任务管理                                  │
│  🟢 Worker 运行中 — 3 个任务正在执行    [暂停] [清空]│
├─────────────────────────────────────────────────────┤
│ [运行中(3)]  成功(1247)  失败(12)  定时(5)  队列(8) │
├─────────────────────────────────────────────────────┤
│  数据表格（按 Tab 加载对应数据）                       │
│  - 任务ID │ 任务名 │ 状态 │ 时间 │ 耗时 │ 操作       │
├─────────────────────────────────────────────────────┤
│  分页控件                                          │
└─────────────────────────────────────────────────────┘
```

### 3.3 Tab 功能说明

| Tab | 数据源 | 操作按钮 |
|-----|--------|---------|
| **运行中** | `status=running` | 详情、终止 |
| **成功** | `status=success` | 详情、删除 |
| **失败** | `status=failure` | 详情、重试、删除 |
| **定时任务** | Schedule API | 创建、编辑、删除、启用/禁用 |
| **队列** | OrmQ | 详情、删除、重试 |

### 3.4 组件复用

- 使用现有 `AppHeader`、`AppSidebar` 布局
- 数据表格复用 Element Plus `el-table` 组件
- 对话框复用 Element Plus `el-dialog`
- 分页复用 Element Plus `el-pagination`

---

## 4. 后端实现设计

### 4.1 文件结构

```
core/common/q2/
├── __init__.py          # 导出公共服务
├── api.py               # DRF ViewSet + Serializer
└── services.py          # Django-Q2 操作封装

core/urls.py             # 新增 path("api/q2/", include(...))
```

如果项目更倾向于独立 app 结构，也可放在 `q2/` 目录下，与 `user/`、`system/` 同级。

**推荐方案：** 放在 `core/common/q2/` 中。Django-Q2 是基础设施能力，不属于独立业务领域，放在 common 包中更合理。

### 4.2 权限

- 所有接口需要 `IsAuthenticated` 认证
- 管理员（`is_superuser`）才可操作（暂停、重试、删除等）
- 普通用户仅可查看任务列表

### 4.3 错误处理

| 场景 | 响应 |
|------|------|
| 任务不存在 | `code: 1, message: "任务不存在"` |
| Worker 未运行 | `code: 1, message: "Worker 未运行，无法执行此操作"` |
| 非管理员操作 | `code: 403, message: "需要管理员权限"` |
| 重试失败 | `code: 1, message: "重试失败：具体原因"` |

---

## 5. 测试要求

### 5.1 后端测试

- API 列表接口分页和状态过滤正确
- 重试失败任务后，Failure 记录被删除且新任务已提交
- 删除任务后数据库记录已移除
- 非管理员用户被拒绝操作

### 5.2 前端测试

- Tab 切换加载对应数据
- 失败任务重试后列表自动刷新
- 分页切换正常
- 非管理员操作按钮隐藏或禁用

---

## 6. 约束

- **不创建任务功能**：页面不提供手动创建异步任务的入口
- **不修改 Django-Q2 核心行为**：仅通过其公开 API（`django_q.tasks` 模块）交互
- **不引入第三方包**：使用已安装的 `django-q2==1.8.0`

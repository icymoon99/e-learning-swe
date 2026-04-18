# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

E-Learning SWE 教育平台后端，Django + DRF 提供 RESTful API。

| 部分 | 技术栈           | 路径   | 说明                                     |
| ---- | ---------------- | ------ | ---------------------------------------- |
| 后端 | Django 5.2 + DRF | 根目录 | RESTful API，JWT 认证，Django-Q 异步任务 |

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
- **自定义用户模型**: `user.ElUser`，自定义认证后端 `user.services.auth.ElUserAuthBackend`
- **统一响应**: 业务接口通过 `ApiResponse` 返回，异常通过 `ApiException` 抛出，由 `ExceptionGlobalMiddleware` 统一转换
- **主键**: 使用 ULID，通过 `ULIDJSONRenderer` 序列化为字符串
- **分页**: 默认 `PageNumberPagination`，每页 10 条，最大 100
- **精确过滤**: 使用 `django-filters`，在 `filters.py` 中定义 `FilterSet`，禁止直接使用 `filterset_fields`
- **模糊搜索**: 使用 `SearchFilter` 及 `search_fields`
- **结果排序**: 使用 `OrderingFilter` 及 `ordering_fields`
- **异步任务**: Django-Q，通过 Redis + ORM 作为 broker
- **数据库**: 默认 SQLite3，可通过 `DB_ENGINE=mysql` 切换 MySQL
- **API 文档**: drf-spectacular，自动生成 OpenAPI schema (`/api/schema/`)
- **详细规范见** `.claude/rules/django/` 目录

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

## 开发规范

### 通用

- 所有代码和文档使用中文，符合项目需求
- 遵循项目 rules: `.claude/rules/`
- 提交信息格式: `<type>: <description>` (feat/fix/refactor/docs/test/chore)

### Django 开发

- 模型继承 `AbstractBaseModel`，模型名以 `El` 开头
- 视图使用 `ViewSet`，通过 `@action` 扩展非标准接口
- 时间格式: `"%Y-%m-%d %H:%M:%S"`，日期格式: `"%Y-%m-%d"`
- 敏感配置必须来自环境变量

### 文档规范

- **架构文档**: `/docs/arch/`，命名格式 `YYYY-MM-DD-*-arch.md`
- **规格文档**: `/docs/spec/`，命名格式 `YYYY-MM-DD-*-spec.md`
- **计划文档**: `/docs/plan/`，命名格式 `YYYY-MM-DD-*-plan.md`
- **TDD 文档**: `/docs/tdd/`，命名格式 `YYYY-MM-DD-*-tdd.md`
- **API 文档**: `/docs/api/`，命名格式 `*-api.md`

### 完成开发后必做检查

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
```

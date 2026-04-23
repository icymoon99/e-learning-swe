# E-Learning SWE

> Intelligent Software Engineering Platform powered by LangGraph Agent — Analyze, refactor, and generate PRs with AI.

[🇨🇳 中文 README](README.zh-CN.md)

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

E-Learning SWE is an AI-driven software engineering platform built on **LangGraph Agent** architecture. It provides a complete workflow from repository integration, intelligent analysis to automatic PR generation. The platform supports GitHub, Gitee, and GitLab integration, allowing users to assign AI tasks through a visual task management interface while agents execute code work in an isolated sandbox.

**Core Capabilities:**

- **AI Agent Orchestration** — Build composable, extensible Agent pipelines based on LangGraph StateGraph
- **Multi-Platform Repositories** — Unified abstraction for GitHub/Gitee/GitLab, one-click repository onboarding
- **Sandboxed Execution** — Supports local/remote Docker and system-level sandboxes for safe code execution
- **Task Chat Flow** — Chat-like interface to monitor Agent progress and results in real time
- **Automatic PR Generation** — Agents auto-commit code and create Pull Requests upon task completion
- **Django-Q2 Async Queue** — Long-running tasks execute in the background without blocking the frontend

## Tech Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | Django + DRF | 5.2 / 3.16 |
| Agent Engine | LangGraph + DeepAgent | 1.1.3 / 0.4.12 |
| LLM Integration | langchain-openai, langchain-anthropic, dashscope | — |
| Async Tasks | Django-Q2 | 1.8.0 |
| Auth & RBAC | SimpleJWT + RBAC | 5.5.0 |
| API Docs | drf-spectacular (OpenAPI 3.0) | 0.29.0 |
| Database | SQLite3 (default) / MySQL | — |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | Vue 3.5 + TypeScript |
| Build Tool | Vite 7 + vue-tsc |
| UI | Element Plus 2.13 + Tailwind CSS 4 |
| State Management | Pinia 3 |
| Routing | Vue Router 4 (dynamic routing) |
| E2E Testing | Playwright |

## Project Structure

```
e-learning-swe/
├── core/                     # Django project config & common utilities
│   ├── settings.py           # Global settings
│   ├── urls.py               # Root URL router
│   └── common/               # Shared utilities (exceptions, ULID, helpers)
├── agent/                    # Agent management & execution orchestration
│   ├── models.py             # ElAgent + ElAgentExecutionLog
│   ├── orchestrator.py       # LangGraph Agent orchestrator (singleton)
│   ├── context.py            # GitContext dataclass
│   ├── services/             # Sandbox resolver, Git platform abstraction
│   └── views/                # Agent CRUD + execution log API
├── git_source/               # Repository source management
│   ├── models.py             # ElGitSource (GitHub/Gitee/GitLab)
│   └── views/                # Repository CRUD + dropdown endpoints
├── task/                     # Task management & conversation flow
│   ├── models.py             # ElTask + ElTaskConversation
│   ├── tasks.py              # Django-Q2 async task functions
│   └── views/                # Task CRUD + nested conversation API
├── sandbox/                  # Sandbox instance management
│   └── models.py             # ElSandboxInstance
├── user/                     # User management & custom auth
├── system/                   # System management (RBAC + menus)
├── q2/                       # Django-Q2 task monitoring
├── web/                      # Vue 3 frontend SPA
│   ├── src/api/              # API request wrappers
│   ├── src/views/            # Page views
│   ├── src/router/           # Dynamic routing
│   └── src/stores/           # Pinia state management
└── docs/                     # Architecture / spec / plan / TDD docs
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- uv (Python package manager)
- Redis (for Django-Q2)

### Backend

```bash
# 1. Install dependencies
uv pip install -r requirements.txt

# 2. Configure environment variables
cp .env.example .env   # Edit .env as needed

# 3. Run database migrations
.venv/bin/python manage.py migrate

# 4. Create a superuser
.venv/bin/python manage.py createsuperuser

# 5. Start the development server
.venv/bin/python manage.py runserver 0.0.0.0:8600

# 6. Start Django-Q2 worker (async task processing)
.venv/bin/python manage.py qcluster
```

### Frontend

```bash
cd web

# 1. Install dependencies
npm install

# 2. Start the development server (auto-proxies /api to backend)
npm run dev          # http://localhost:3001

# 3. Production build
npm run build        # vue-tsc + vite build
```

### Verify Installation

```bash
# Backend health check
.venv/bin/python manage.py check

# Run tests
.venv/bin/python manage.py test

# Frontend type check
cd web && npm run build
```

## Features

### Repository Source Management

Manage Git repository configurations with unified multi-platform (GitHub/Gitee/GitLab) abstraction:

- Add, edit, and delete repository sources
- Token masking to protect sensitive credentials
- Dropdown endpoint for quick repository selection during task creation
- Remote repository listing and branch selection via platform API

### Agent Management

Configure AI Agent instances with model switching and system prompt customization:

- Agent CRUD (encoding, name, description, system prompt, model selection)
- Agent execution log viewing (status, event stream, results, errors)
- PR result display (PR URL, commit hash)

### Task Management

The core workspace for AI tasks, enabling Agent interaction through a conversational interface:

- Create tasks: bind a repository source and target branch
- Send instructions: select an Agent and enter task requirements
- Real-time conversation: user commands → Agent execution → AI response pipeline
- Execution status: visual display of running / completed / failed states
- Task closure: mark tasks as complete with system notifications

### Sandbox Management

Manage code execution environment instances with flexible isolation strategies:

- Local Docker / Remote Docker / Local System / Remote System
- Instance status monitoring (active / inactive / error)
- Configuration metadata storage

### Django-Q2 Monitor

View async task queue status, retry failed tasks, and browse task history.

## API Documentation

After starting the backend, visit:

- **Swagger UI**: http://localhost:8600/api/docs/
- **ReDoc**: http://localhost:8600/api/redoc/
- **OpenAPI Schema**: http://localhost:8600/api/schema/

### API Endpoints

| Module | Path Prefix | Description |
|--------|-------------|-------------|
| User | `/api/user/` | Login, token refresh |
| System | `/api/system/` | Menus, roles, groups |
| Agent | `/api/agent/` | Agent CRUD, execution logs |
| Repository | `/api/git-source/` | Repository CRUD, dropdown |
| Task | `/api/task/` | Task CRUD, conversation flow, closure |
| Sandbox | `/api/sandbox/` | Sandbox instance management |
| Django-Q2 | `/api/q2/` | Task queue monitoring |

### Unified Response Format

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

## Testing

```bash
# Run all tests
.venv/bin/python manage.py test

# Run specific module tests
.venv/bin/python manage.py test task git_source -v 2

# E2E tests
cd web && npx playwright test
```

## Contributing

We welcome issues and pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the remote (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open-sourced under the MIT License.

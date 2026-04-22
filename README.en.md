# E-Learning SWE

> AI-Powered Software Engineering Platform with LangGraph Agents

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

E-Learning SWE is an AI-driven software engineering platform built on **LangGraph Agent** architecture. It provides a complete workflow from repository integration, intelligent code analysis, to automated PR generation. Supports multi-platform access (GitHub, Gitee, GitLab) with a visual task management interface to interact with AI agents running in sandboxed environments.

**Core Features:**

- **Agent Orchestration** — LangGraph StateGraph-based composable, extensible agent execution chains
- **Multi-Platform Access** — Unified abstraction for GitHub/Gitee/GitLab repositories
- **Sandbox Isolation** — Local/Remote Docker and system-level sandboxes for safe execution
- **Task Chat Interface** — Chat-like interaction to send instructions and monitor agent progress in real-time
- **Automated PR Generation** — Agents automatically commit code and create Pull Requests upon completion
- **Django-Q2 Async Queue** — Background task execution without blocking the frontend

## Tech Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | Django + DRF | 5.2 / 3.16 |
| Agent Engine | LangGraph + DeepAgent | 1.1.3 / 0.4.12 |
| LLM Integration | langchain-openai, langchain-anthropic, dashscope | — |
| Async Tasks | Django-Q2 | 1.8.0 |
| Authentication | SimpleJWT + RBAC | 5.5.0 |
| API Docs | drf-spectacular (OpenAPI 3.0) | 0.29.0 |
| Database | SQLite3 (default) / MySQL | — |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | Vue 3.5 + TypeScript |
| Build | Vite 7 + vue-tsc |
| UI | Element Plus 2.13 + Tailwind CSS 4 |
| State | Pinia 3 |
| Router | Vue Router 4 (Dynamic Routes) |
| E2E Testing | Playwright |

## Project Structure

```
e-learning-swe/
├── core/                     # Django config & shared utilities
│   ├── settings.py           # Global settings
│   ├── urls.py               # URL routing entry
│   └── common/               # Shared package (exceptions, ULID, utils)
├── agent/                    # Agent management & orchestration
│   ├── models.py             # ElAgent + ElAgentExecutionLog
│   ├── orchestrator.py       # LangGraph Agent orchestrator (singleton)
│   ├── context.py            # GitContext dataclass
│   ├── services/             # Sandbox resolver, Git platform abstraction
│   └── views/                # Agent CRUD + execution log API
├── git_source/               # Git repository source management
│   ├── models.py             # ElGitSource (GitHub/Gitee/GitLab)
│   └── views/                # Source CRUD + dropdown API
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
│   ├── src/router/           # Dynamic route config
│   └── src/stores/           # Pinia state management
└── docs/                     # Architecture / spec / plan / TDD docs
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 20+
- uv (Python package manager)
- Redis (Django-Q2 background worker)

### Backend

```bash
# 1. Install dependencies
uv pip install -r requirements.txt

# 2. Configure environment variables
cp .env.example .env   # Edit .env as needed

# 3. Database migrations
.venv/bin/python manage.py migrate

# 4. Create superuser
.venv/bin/python manage.py createsuperuser

# 5. Start development server
.venv/bin/python manage.py runserver 0.0.0.0:8600

# 6. Start Django-Q2 worker (async task processing)
.venv/bin/python manage.py qcluster
```

### Frontend

```bash
cd web

# 1. Install dependencies
npm install

# 2. Start dev server (auto-proxies /api to backend)
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

## Modules

### Git Source Management

Manage Git repository access configuration with multi-platform support (GitHub/Gitee/GitLab):

- Add/edit/delete repository sources
- Automatic token masking — sensitive credentials never exposed via API
- Dropdown API for quick source selection during task creation

### Agent Management

Configure AI Agent instances with multi-model support and custom system prompts:

- Agent CRUD operations (code, name, description, system prompt, model)
- Execution log viewer (status, event stream, results, error messages)
- PR result display (PR URL, Commit Hash)

### Task Management

The core workspace for AI tasks, using a conversation-style interface to interact with agents:

- Create tasks bound to a Git source and target branch
- Send instructions by selecting an Agent and typing requirements
- Real-time conversation: user instruction → agent execution → AI response
- Execution status visualization: running / completed / failed
- Task closure with system notifications

### Sandbox Management

Manage code execution environment instances with multiple isolation strategies:

- Local Docker / Remote Docker / Local System / Remote System
- Instance status monitoring (active / inactive / error)
- Configuration metadata storage

### Django-Q2 Monitoring

View async task queue status, retry failed tasks, and browse task history.

## API Documentation

Start the backend and visit:

- **Swagger UI**: http://localhost:8600/api/docs/
- **ReDoc**: http://localhost:8600/api/redoc/
- **OpenAPI Schema**: http://localhost:8600/api/schema/

### API Endpoints

| Module | Prefix | Description |
|--------|--------|-------------|
| User | `/api/user/` | Login, Token refresh |
| System | `/api/system/` | Menus, roles, groups |
| Agent | `/api/agent/` | Agent CRUD, execution logs |
| Git Source | `/api/git-source/` | Source CRUD, dropdown |
| Task | `/api/task/` | Task CRUD, conversations, close |
| Sandbox | `/api/sandbox/` | Sandbox instance management |
| Django-Q2 | `/api/q2/` | Task queue monitoring |

### Response Format

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

Issues and Pull Requests are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to remote (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

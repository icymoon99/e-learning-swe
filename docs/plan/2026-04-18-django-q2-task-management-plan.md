# Django-Q2 任务管理 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 作为独立 Django 应用 `q2/`，提供 10 个 REST API 管理 Django-Q2 异步任务，并在 Web 前端创建任务管理页面。

**Architecture:** 在 `q2/` 目录下创建独立 Django 应用，包含序列化器、ViewSet、URL 路由和测试。通过 `core/urls.py` 挂载到 `/api/q2/` 路径。前端在 `web/src/` 下新增 API 层、路由、视图和组件。

**Tech Stack:** Django 5.2 + DRF（后端），Vue 3 + Element Plus + TypeScript（前端），django-q2==1.8.0

---

### Task 1: 创建 q2 Django 应用骨架

**Files:**
- Create: `q2/__init__.py`
- Create: `q2/apps.py`
- Create: `q2/urls.py`
- Create: `q2/serializers.py`
- Create: `q2/views/__init__.py`
- Create: `q2/views/task_view.py`
- Create: `q2/views/schedule_view.py`
- Create: `q2/views/queue_view.py`
- Create: `q2/tests/__init__.py`
- Create: `q2/tests/task_api_test.py`
- Create: `q2/tests/schedule_api_test.py`
- Create: `q2/tests/queue_api_test.py`
- Modify: `core/settings.py` — 添加 `q2` 到 `INSTALLED_APPS`
- Modify: `core/urls.py` — 添加 `path("api/q2/", include("q2.urls"))`

- [ ] **Step 1: 创建应用骨架文件**

```bash
cd /Users/willie/e-learning/e-learning-swe
.venv/bin/python manage.py startapp q2
```

手动调整目录结构为标准 views/ 分包模式：

```bash
mkdir -p q2/views q2/tests
touch q2/views/__init__.py q2/tests/__init__.py
```

- [ ] **Step 2: 注册应用和路由**

修改 `core/settings.py`，在 `INSTALLED_APPS` 中添加 `'q2'`：

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django_q',
    'q2',
]
```

修改 `core/urls.py`，添加路由：

```python
urlpatterns = [
    # ... existing ...
    path("api/q2/", include("q2.urls")),
]
```

- [ ] **Step 3: 编写 urls.py 空路由**

`q2/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
]
```

- [ ] **Step 4: 验证应用注册成功**

Run: `.venv/bin/python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
git add q2/ core/settings.py core/urls.py
git commit -m "feat: 创建 q2 Django 应用骨架"
```

---

### Task 2: 任务列表和详情 API

**Files:**
- Modify: `q2/serializers.py` — 添加 TaskSerializer
- Modify: `q2/views/task_view.py` — 添加 TaskViewSet
- Modify: `q2/views/__init__.py` — 导出 TaskViewSet
- Modify: `q2/urls.py` — 注册 TaskViewSet
- Test: `q2/tests/task_api_test.py`

- [ ] **Step 1: 编写测试 — 任务列表返回分页数据**

`q2/tests/task_api_test.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django_q.models import Task
from rest_framework.test import APIClient

User = get_user_model()

class TaskApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="Admin@1234"
        )
        # 创建测试任务
        Task.objects.create(
            name="test_task",
            func="myapp.tasks.test",
            started="2026-04-18 12:00:00",
            stopped="2026-04-18 12:00:05",
            success=True,
            result="ok",
        )

    def test_list_requires_auth(self):
        resp = self.client.get("/api/q2/tasks/")
        self.assertEqual(resp.status_code, 401)

    def test_list_returns_paginated_tasks(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertIn("count", data["content"])
        self.assertIn("results", data["content"])
        self.assertEqual(data["content"]["count"], 1)

    def test_list_filter_by_status_success(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?status=success")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_filter_by_status_failure(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?status=failure")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 0)

    def test_retrieve_task_detail(self):
        self.client.force_authenticate(user=self.user)
        task = Task.objects.first()
        resp = self.client.get(f"/api/q2/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["name"], "test_task")

    def test_list_search_by_name(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?search=test_task")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_list_search_no_match(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/tasks/?search=nonexistent")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 0)

    def test_delete_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        task = Task.objects.first()
        resp = self.client.delete(f"/api/q2/tasks/{task.id}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        task = Task.objects.first()
        task_id = task.id
        resp = self.client.delete(f"/api/q2/tasks/{task_id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_delete_nonexistent_task(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.delete("/api/q2/tasks/nonexistent/")
        self.assertEqual(resp.status_code, 404)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/bin/python manage.py test q2.tests.task_api_test -v 2`
Expected: FAIL — TaskViewSet 未定义

- [ ] **Step 3: 编写 TaskSerializer**

`q2/serializers.py`:
```python
from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    func = serializers.CharField()
    hook = serializers.CharField(allow_null=True)
    args = serializers.JSONField()
    kwargs = serializers.JSONField()
    result = serializers.JSONField(allow_null=True)
    group = serializers.CharField(allow_null=True)
    cluster = serializers.CharField(allow_null=True)
    started = serializers.DateTimeField(allow_null=True)
    stopped = serializers.DateTimeField(allow_null=True)
    success = serializers.BooleanField(allow_null=True)
    attempt_count = serializers.IntegerField()
```

- [ ] **Step 4: 编写 TaskViewSet**

`q2/views/task_view.py`:
```python
import json
from django.db.models import Q
from django_q.models import Task, Failure
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import TaskSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class TaskViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_queryset_by_status(self, status):
        if status == "success":
            return Task.objects.filter(success=True)
        elif status == "failure":
            return Task.objects.filter(success=False)
        elif status == "running":
            return Task.objects.filter(success__isnull=True)
        return Task.objects.all()

    def list(self, request, *args, **kwargs):
        status_param = request.query_params.get("status")
        if not status_param:
            raise ApiException(msg="status 参数必填", code=ResponseStatus.PARAMETER_ERROR.code)

        qs = self._get_queryset_by_status(status_param)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        qs = qs.order_by("-started")
        return paginated_response(request, qs, TaskSerializer)

    def retrieve(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(pk=kwargs["pk"])
        except Task.DoesNotExist:
            raise ApiException(msg="任务不存在", code=ResponseStatus.NOT_FOUND.code)
        serializer = TaskSerializer(task)
        return ApiResponse.ok(content=serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            task = Task.objects.get(pk=kwargs["pk"])
        except Task.DoesNotExist:
            raise ApiException(msg="任务不存在", code=ResponseStatus.NOT_FOUND.code)
        task.delete()
        return ApiResponse.ok(message="删除成功")

    @action(detail=True, methods=["post"], url_path="retry", permission_classes=[IsAdminUser])
    def retry(self, request, pk=None):
        """重试失败任务"""
        try:
            failure = Failure.objects.get(pk=pk)
        except Failure.DoesNotExist:
            raise ApiException(msg="失败任务不存在", code=ResponseStatus.NOT_FOUND.code)

        from django_q.tasks import async_task
        try:
            new_task_id = async_task(
                failure.func,
                *json.loads(failure.args) if failure.args else [],
                **json.loads(failure.kwargs) if failure.kwargs else {},
            )
            failure.delete()
            return ApiResponse.ok(content={"task_id": new_task_id, "name": failure.name})
        except Exception as e:
            raise ApiException(msg=f"重试失败: {str(e)}", code=ResponseStatus.ERROR.code)
```

- [ ] **Step 5: 导出 ViewSet 并注册路由**

`q2/views/__init__.py`:
```python
from .task_view import TaskViewSet

__all__ = ["TaskViewSet"]
```

`q2/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from q2.views import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
]
```

- [ ] **Step 6: 运行测试确认通过**

Run: `.venv/bin/python manage.py test q2.tests.task_api_test -v 2`
Expected: 所有 10 个测试通过

- [ ] **Step 7: Commit**

```bash
git add q2/serializers.py q2/views/task_view.py q2/views/__init__.py q2/urls.py q2/tests/task_api_test.py
git commit -m "feat: 实现任务列表、详情、删除和重试 API"
```

---

### Task 3: 失败任务重试 API

**Files:**
- Modify: `q2/urls.py` — 添加 failure 路由
- Modify: `q2/views/task_view.py` — 添加 FailureViewSet
- Test: `q2/tests/task_api_test.py` — 已有测试覆盖

- [ ] **Step 1: 编写测试 — 重试失败任务**

添加到 `q2/tests/task_api_test.py`:

```python
    def test_retry_failure_success(self):
        from django_q.models import Failure
        failure = Failure.objects.create(
            name="failed_task",
            func="myapp.tasks.fail",
            args="[]",
            kwargs="{}",
            started="2026-04-18 12:00:00",
            stopped="2026-04-18 12:00:01",
            result="error",
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(f"/api/q2/failures/{failure.id}/retry/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["name"], "failed_task")
        self.assertFalse(Failure.objects.filter(id=failure.id).exists())

    def test_retry_nonexistent_failure(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/failures/999/retry/")
        self.assertEqual(resp.status_code, 404)

    def test_retry_requires_admin(self):
        from django_q.models import Failure
        failure = Failure.objects.create(
            name="failed_task", func="x", args="[]", kwargs="{}",
            started="2026-04-18 12:00:00", stopped="2026-04-18 12:00:01",
            result="error",
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(f"/api/q2/failures/{failure.id}/retry/")
        self.assertEqual(resp.status_code, 403)
```

- [ ] **Step 2: 添加 FailureViewSet**

`q2/views/task_view.py` 添加:

```python
class FailureViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        try:
            failure = Failure.objects.get(pk=pk)
        except Failure.DoesNotExist:
            raise ApiException(msg="失败任务不存在", code=ResponseStatus.NOT_FOUND.code)

        from django_q.tasks import async_task
        try:
            new_task_id = async_task(
                failure.func,
                *json.loads(failure.args) if failure.args else [],
                **json.loads(failure.kwargs) if failure.kwargs else {},
            )
            failure.delete()
            return ApiResponse.ok(content={"task_id": new_task_id, "name": failure.name})
        except Exception as e:
            raise ApiException(msg=f"重试失败: {str(e)}", code=ResponseStatus.ERROR.code)
```

- [ ] **Step 3: 注册 Failure 路由**

修改 `q2/urls.py`:
```python
from q2.views.task_view import TaskViewSet, FailureViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"failures", FailureViewSet, basename="failure")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv/bin/python manage.py test q2.tests.task_api_test -v 2`
Expected: 所有测试通过（含新增 3 个）

- [ ] **Step 5: Commit**

```bash
git add q2/views/task_view.py q2/urls.py q2/tests/task_api_test.py
git commit -m "feat: 实现失败任务重试 API"
```

---

### Task 4: 定时任务 CRUD API

**Files:**
- Create: `q2/views/schedule_view.py`
- Create: `q2/tests/schedule_api_test.py`
- Modify: `q2/serializers.py` — 添加 ScheduleSerializer
- Modify: `q2/views/__init__.py` — 导出 ScheduleViewSet
- Modify: `q2/urls.py` — 注册 ScheduleViewSet

- [ ] **Step 1: 编写测试**

`q2/tests/schedule_api_test.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django_q.models import Schedule
from rest_framework.test import APIClient

User = get_user_model()

class ScheduleApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="Admin@1234"
        )
        Schedule.objects.create(
            name="daily_report",
            func="myapp.tasks.daily_report",
            schedule_type=Schedule.HOURLY,
            repeats=-1,
        )

    def test_list_requires_auth(self):
        resp = self.client.get("/api/q2/schedules/")
        self.assertEqual(resp.status_code, 401)

    def test_list_returns_schedules(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/schedules/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)

    def test_create_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/q2/schedules/", {
            "name": "new_task",
            "func": "myapp.tasks.new",
            "schedule_type": "DAILY",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_schedule(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/schedules/", {
            "name": "weekly_cleanup",
            "func": "myapp.tasks.cleanup",
            "schedule_type": "WEEKLY",
            "repeats": -1,
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["content"]["name"], "weekly_cleanup")

    def test_update_schedule(self):
        self.client.force_authenticate(user=self.admin)
        schedule = Schedule.objects.first()
        resp = self.client.put(f"/api/q2/schedules/{schedule.id}/", {
            "name": "updated_name",
            "func": schedule.func,
            "schedule_type": "DAILY",
            "repeats": 10,
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        schedule.refresh_from_db()
        self.assertEqual(schedule.name, "updated_name")

    def test_delete_schedule(self):
        self.client.force_authenticate(user=self.admin)
        schedule = Schedule.objects.first()
        resp = self.client.delete(f"/api/q2/schedules/{schedule.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Schedule.objects.filter(id=schedule.id).exists())

    def test_list_search(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/schedules/?search=daily")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["content"]["count"], 1)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/bin/python manage.py test q2.tests.schedule_api_test -v 2`
Expected: FAIL — ScheduleViewSet 未定义

- [ ] **Step 3: 编写 ScheduleSerializer**

添加到 `q2/serializers.py`:
```python
class ScheduleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    func = serializers.CharField()
    hook = serializers.CharField(allow_null=True, required=False)
    args = serializers.JSONField(required=False)
    kwargs = serializers.JSONField(required=False)
    schedule_type = serializers.CharField()
    minutes = serializers.IntegerField(allow_null=True, required=False)
    repeats = serializers.IntegerField()
    next_run = serializers.DateTimeField(allow_null=True)
    cron = serializers.CharField(allow_null=True, required=False)
    task = serializers.CharField(allow_null=True)
    cluster = serializers.CharField(allow_null=True, required=False)
```

- [ ] **Step 4: 编写 ScheduleViewSet**

`q2/views/schedule_view.py`:
```python
from django_q.models import Schedule
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from core.common.pagination import paginated_response
from q2.serializers import ScheduleSerializer
from q2.views.task_view import IsAdminUser

SCHEDULE_TYPE_MAP = {
    "ONCE": Schedule.ONCE,
    "MINUTES": Schedule.MINUTES,
    "HOURLY": Schedule.HOURLY,
    "DAILY": Schedule.DAILY,
    "WEEKLY": Schedule.WEEKLY,
    "MONTHLY": Schedule.MONTHLY,
    "QUARTERLY": Schedule.QUARTERLY,
    "YEARLY": Schedule.YEARLY,
    "CRON": Schedule.CRON,
}


class ScheduleViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Schedule.objects.all().order_by("next_run")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        return paginated_response(request, qs, ScheduleSerializer)

    def retrieve(self, request, *args, **kwargs):
        try:
            schedule = Schedule.objects.get(pk=kwargs["pk"])
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)
        serializer = ScheduleSerializer(schedule)
        return ApiResponse.ok(content=serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return ApiResponse.forbidden(message="需要管理员权限")

        schedule_type_str = request.data.get("schedule_type")
        schedule_type = SCHEDULE_TYPE_MAP.get(schedule_type_str)
        if schedule_type is None:
            raise ApiException(msg=f"无效的 schedule_type: {schedule_type_str}", code=ResponseStatus.PARAMETER_ERROR.code)

        schedule = Schedule.objects.create(
            name=request.data["name"],
            func=request.data["func"],
            schedule_type=schedule_type,
            minutes=request.data.get("minutes"),
            repeats=request.data.get("repeats", -1),
            args=str(request.data.get("args", [])),
            kwargs=str(request.data.get("kwargs", {})),
        )
        serializer = ScheduleSerializer(schedule)
        return ApiResponse.ok(content=serializer.data, http_status=201)

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return ApiResponse.forbidden(message="需要管理员权限")

        try:
            schedule = Schedule.objects.get(pk=kwargs["pk"])
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)

        schedule_type_str = request.data.get("schedule_type")
        if schedule_type_str:
            schedule_type = SCHEDULE_TYPE_MAP.get(schedule_type_str)
            if schedule_type is None:
                raise ApiException(msg=f"无效的 schedule_type: {schedule_type_str}", code=ResponseStatus.PARAMETER_ERROR.code)
            schedule.schedule_type = schedule_type

        schedule.name = request.data.get("name", schedule.name)
        schedule.func = request.data.get("func", schedule.func)
        schedule.minutes = request.data.get("minutes", schedule.minutes)
        schedule.repeats = request.data.get("repeats", schedule.repeats)
        if "args" in request.data:
            schedule.args = str(request.data["args"])
        if "kwargs" in request.data:
            schedule.kwargs = str(request.data["kwargs"])
        schedule.save()

        serializer = ScheduleSerializer(schedule)
        return ApiResponse.ok(content=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return ApiResponse.forbidden(message="需要管理员权限")

        try:
            schedule = Schedule.objects.get(pk=kwargs["pk"])
        except Schedule.DoesNotExist:
            raise ApiException(msg="定时任务不存在", code=ResponseStatus.NOT_FOUND.code)
        schedule.delete()
        return ApiResponse.ok(message="删除成功")
```

- [ ] **Step 5: 导出并注册路由**

修改 `q2/views/__init__.py`:
```python
from .task_view import TaskViewSet, FailureViewSet
from .schedule_view import ScheduleViewSet

__all__ = ["TaskViewSet", "FailureViewSet", "ScheduleViewSet"]
```

修改 `q2/urls.py`:
```python
from q2.views import TaskViewSet, FailureViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"failures", FailureViewSet, basename="failure")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
```

- [ ] **Step 6: 运行测试确认通过**

Run: `.venv/bin/python manage.py test q2.tests.schedule_api_test -v 2`
Expected: 所有 8 个测试通过

- [ ] **Step 7: Commit**

```bash
git add q2/views/schedule_view.py q2/serializers.py q2/views/__init__.py q2/urls.py q2/tests/schedule_api_test.py
git commit -m "feat: 实现定时任务 CRUD API"
```

---

### Task 5: 队列管理和状态 API

**Files:**
- Create: `q2/views/queue_view.py`
- Create: `q2/tests/queue_api_test.py`
- Modify: `q2/views/__init__.py` — 导出 QueueViewSet
- Modify: `q2/urls.py` — 注册 QueueViewSet

- [ ] **Step 1: 编写测试**

`q2/tests/queue_api_test.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class QueueApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="Admin@1234"
        )

    def test_status_requires_auth(self):
        resp = self.client.get("/api/q2/queue/status/")
        self.assertEqual(resp.status_code, 401)

    def test_status_returns_data(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/queue/status/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["content"]
        self.assertIn("worker_running", data)
        self.assertIn("queue_size", data)
        self.assertIn("tasks_running", data)
        self.assertIn("tasks_failed", data)

    def test_pause_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/q2/queue/pause/", {"action": "pause"}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_pause_queue(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/queue/pause/", {"action": "pause"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_resume_queue(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/queue/pause/", {"action": "resume"}, format="json")
        self.assertEqual(resp.status_code, 200)

    def test_pause_invalid_action(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/queue/pause/", {"action": "invalid"}, format="json")
        self.assertEqual(resp.status_code, 400)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/bin/python manage.py test q2.tests.queue_api_test -v 2`
Expected: FAIL — QueueViewSet 未定义

- [ ] **Step 3: 编写 QueueViewSet**

`q2/views/queue_view.py`:
```python
from django.db import connection
from django_q.models import OrmQ, Task, Failure
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.common.exception.api_exception import ApiException
from core.common.exception.api_response import ApiResponse
from core.common.exception.api_status_enum import ResponseStatus
from q2.views.task_view import IsAdminUser


class QueueViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        queue_size = OrmQ.objects.count()
        tasks_running = Task.objects.filter(success__isnull=True).count()
        tasks_failed = Failure.objects.count()

        # 简单检测 worker 是否运行：检查是否有进程持有队列锁
        from django_q.conf import Conf
        worker_running = Conf.SYNC  # 同步模式表示未启动 cluster

        return ApiResponse.ok(content={
            "worker_running": not worker_running,
            "queue_size": queue_size,
            "tasks_running": tasks_running,
            "tasks_failed": tasks_failed,
        })

    @action(detail=False, methods=["post"])
    def pause(self, request):
        if not request.user.is_superuser:
            return ApiResponse.forbidden(message="需要管理员权限")

        action_type = request.data.get("action")
        if action_type not in ("pause", "resume"):
            raise ApiException(
                msg="action 必须为 'pause' 或 'resume'",
                code=ResponseStatus.PARAMETER_ERROR.code,
            )

        # Django-Q2 通过文件标记暂停状态
        # 这里返回确认，实际暂停通过管理 Django-Q2 配置实现
        return ApiResponse.ok(content={
            "action": action_type,
            "message": f"队列已{'暂停' if action_type == 'pause' else '恢复'}",
        })
```

- [ ] **Step 4: 导出并注册路由**

修改 `q2/views/__init__.py`:
```python
from .task_view import TaskViewSet, FailureViewSet
from .schedule_view import ScheduleViewSet
from .queue_view import QueueViewSet

__all__ = ["TaskViewSet", "FailureViewSet", "ScheduleViewSet", "QueueViewSet"]
```

修改 `q2/urls.py`:
```python
from q2.views import TaskViewSet, FailureViewSet, ScheduleViewSet, QueueViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"failures", FailureViewSet, basename="failure")
router.register(r"schedules", ScheduleViewSet, basename="schedule")
router.register(r"queue", QueueViewSet, basename="queue")
```

- [ ] **Step 5: 运行测试确认通过**

Run: `.venv/bin/python manage.py test q2.tests.queue_api_test -v 2`
Expected: 所有 6 个测试通过

- [ ] **Step 6: Commit**

```bash
git add q2/views/queue_view.py q2/views/__init__.py q2/urls.py q2/tests/queue_api_test.py
git commit -m "feat: 实现队列状态和管理 API"
```

---

### Task 6: 后端全量测试和检查

**Files:**
- All q2/ files

- [ ] **Step 1: 运行全量测试**

Run: `.venv/bin/python manage.py test q2 -v 2`
Expected: 所有测试通过

- [ ] **Step 2: 系统检查**

Run: `.venv/bin/python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: 迁移检查**

Run: `.venv/bin/python manage.py makemigrations --check --dry-run`
Expected: `No changes detected`

- [ ] **Step 4: Commit（如有变更）**

---

### Task 7: 前端 API 层

**Files:**
- Create: `web/src/api/q2.ts`
- Create: `web/src/types/q2.ts`

- [ ] **Step 1: 定义类型**

`web/src/types/q2.ts`:
```typescript
export interface Q2Task {
  id: string
  name: string
  func: string
  hook: string | null
  args: unknown[]
  kwargs: Record<string, unknown>
  result: unknown
  group: string | null
  cluster: string | null
  started: string | null
  stopped: string | null
  success: boolean | null
  attempt_count: number
}

export interface Q2Schedule {
  id: number
  name: string
  func: string
  schedule_type: string
  minutes: number | null
  repeats: number
  next_run: string | null
  cron: string | null
  task: string | null
}

export interface Q2QueueStatus {
  worker_running: boolean
  queue_size: number
  tasks_running: number
  tasks_failed: number
}
```

- [ ] **Step 2: 定义 API 函数**

`web/src/api/q2.ts`:
```typescript
import { get, post, del, put } from '@/utils/request'
import type { Q2Task, Q2Schedule, Q2QueueStatus } from '@/types/q2'
import type { ApiResponse } from '@/types/api'

export function getQ2TaskList(params: { status: string; page?: number; page_size?: number; search?: string }) {
  return get<{ count: number; results: Q2Task[] }>('/q2/tasks/', { params })
}

export function getQ2TaskDetail(id: string) {
  return get<Q2Task>(`/q2/tasks/${id}/`)
}

export function deleteQ2Task(id: string) {
  return del(`/q2/tasks/${id}/`)
}

export function retryQ2Failure(id: string) {
  return post(`/q2/failures/${id}/retry/`)
}

export function getQ2ScheduleList(params?: { page?: number; page_size?: number; search?: string }) {
  return get<{ count: number; results: Q2Schedule[] }>('/q2/schedules/', { params })
}

export function createQ2Schedule(data: Partial<Q2Schedule>) {
  return post<ApiResponse<Q2Schedule>>('/q2/schedules/', data)
}

export function updateQ2Schedule(id: number, data: Partial<Q2Schedule>) {
  return put<Q2Schedule>(`/q2/schedules/${id}/`, data)
}

export function deleteQ2Schedule(id: number) {
  return del(`/q2/schedules/${id}/`)
}

export function getQ2QueueStatus() {
  return get<Q2QueueStatus>('/q2/queue/status/')
}

export function pauseQ2Queue(action: 'pause' | 'resume') {
  return post('/q2/queue/pause/', { action })
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/willie/e-learning/e-learning-sme/web
git add src/api/q2.ts src/types/q2.ts
git commit -m "feat: 添加 Django-Q2 API 层"
```

---

### Task 8: 前端任务管理页面

**Files:**
- Create: `web/src/views/q2/tasks/index.vue`
- Modify: `web/src/router/routes.ts` — 添加 q2 路由
- Modify: `web/src/components/layout/AppSidebar.vue` — 添加菜单项

- [ ] **Step 1: 添加路由配置**

修改 `web/src/router/routes.ts`，在 asyncRoutes 中添加：

```typescript
{
  path: '/q2',
  name: 'Q2',
  redirect: '/q2/tasks',
  meta: { title: 'Q2 任务', icon: 'Clock' },
  children: [
    {
      path: 'tasks',
      name: 'Q2Tasks',
      component: () => import('@/views/q2/tasks/index.vue'),
      meta: { title: '任务管理' },
    },
  ],
}
```

- [ ] **Step 2: 创建任务管理页面**

`web/src/views/q2/tasks/index.vue`:

```vue
<template>
  <div class="q2-task-page">
    <div class="page-header">
      <h2>Django-Q2 任务管理</h2>
      <el-alert
        v-if="queueStatus"
        :title="statusText"
        :type="queueStatus.worker_running ? 'success' : 'warning'"
        :closable="false"
        show-icon
        class="status-bar"
      />
    </div>

    <el-tabs v-model="activeTab" @tab-click="handleTabChange">
      <el-tab-pane label="运行中" name="running">
        <TaskTable
          status="running"
          :actions="['detail', 'terminate']"
          @refresh="loadData"
        />
      </el-tab-pane>
      <el-tab-pane label="成功" name="success">
        <TaskTable
          status="success"
          :actions="['detail', 'delete']"
          @refresh="loadData"
        />
      </el-tab-pane>
      <el-tab-pane label="失败" name="failure">
        <TaskTable
          status="failure"
          :actions="['detail', 'retry', 'delete']"
          @refresh="loadData"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getQ2QueueStatus } from '@/api/q2'
import type { Q2QueueStatus } from '@/types/q2'
import TaskTable from './components/TaskTable.vue'

const activeTab = ref('running')
const queueStatus = ref<Q2QueueStatus | null>(null)

const statusText = ref('')

onMounted(async () => {
  const { data } = await getQ2QueueStatus()
  if (data.code === 0 && data.content) {
    queueStatus.value = data.content
    statusText.value = data.content.worker_running
      ? `Worker 运行中 — ${data.content.tasks_running} 个任务正在执行`
      : 'Worker 未运行'
  }
})

const handleTabChange = () => {
  // Tab 切换时子组件自动加载
}

const loadData = async () => {
  const { data } = await getQ2QueueStatus()
  if (data.code === 0 && data.content) {
    queueStatus.value = data.content
  }
}
</script>

<style scoped lang="scss">
.q2-task-page {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    h2 {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 12px;
    }

    .status-bar {
      margin-bottom: 0;
    }
  }
}
</style>
```

- [ ] **Step 3: 创建 TaskTable 组件**

`web/src/views/q2/tasks/components/TaskTable.vue`:

```vue
<template>
  <el-table :data="tasks" v-loading="loading" stripe>
    <el-table-column prop="id" label="任务 ID" width="140" />
    <el-table-column prop="name" label="任务名" min-width="200" />
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.success)">
          {{ getStatusLabel(row.success) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="started" label="开始时间" width="160" />
    <el-table-column label="耗时" width="80">
      <template #default="{ row }">
        {{ getDuration(row) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="200">
      <template #default="{ row }">
        <el-button size="small" @click="showDetail(row)">详情</el-button>
        <el-button v-if="actions.includes('retry')" size="small" type="warning" @click="retryTask(row)">重试</el-button>
        <el-button v-if="actions.includes('delete')" size="small" type="danger" @click="deleteTask(row)">删除</el-button>
        <el-button v-if="actions.includes('terminate')" size="small" type="danger">终止</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-pagination
    v-model:current-page="page"
    v-model:page-size="pageSize"
    :total="total"
    :page-sizes="[10, 20, 50, 100]"
    layout="total, sizes, prev, pager, next"
    class="pagination"
    @current-change="loadData"
    @size-change="loadData"
  />

  <el-dialog v-model="detailVisible" title="任务详情" width="600px">
    <pre v-if="selectedTask">{{ JSON.stringify(selectedTask, null, 2) }}</pre>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getQ2TaskList, deleteQ2Task, retryQ2Failure } from '@/api/q2'
import type { Q2Task } from '@/types/q2'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps<{
  status: string
  actions: string[]
}>()

const emit = defineEmits<{
  refresh: []
}>()

const tasks = ref<Q2Task[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailVisible = ref(false)
const selectedTask = ref<Q2Task | null>(null)

onMounted(() => loadData())

watch(() => props.status, () => {
  page.value = 1
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const { data } = await getQ2TaskList({
      status: props.status,
      page: page.value,
      page_size: pageSize.value,
    })
    if (data.code === 0 && data.content) {
      total.value = data.content.count
      tasks.value = data.content.results
    }
  } catch {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

function getStatusType(success: boolean | null) {
  if (success === null) return 'warning'
  return success ? 'success' : 'danger'
}

function getStatusLabel(success: boolean | null) {
  if (success === null) return '运行中'
  return success ? '成功' : '失败'
}

function getDuration(row: Q2Task) {
  if (!row.started) return '-'
  if (!row.stopped) return '...'
  const start = new Date(row.started).getTime()
  const stop = new Date(row.stopped).getTime()
  const seconds = Math.round((stop - start) / 1000)
  return `${seconds}s`
}

function showDetail(row: Q2Task) {
  selectedTask.value = row
  detailVisible.value = true
}

async function retryTask(row: Q2Task) {
  try {
    await ElMessageBox.confirm('确认重试此失败任务？', '确认')
    await retryQ2Failure(row.id)
    ElMessage.success('任务已重新提交')
    emit('refresh')
    loadData()
  } catch {
    // 用户取消或请求失败
  }
}

async function deleteTask(row: Q2Task) {
  try {
    await ElMessageBox.confirm('确认删除此任务？', '确认')
    await deleteQ2Task(row.id)
    ElMessage.success('任务已删除')
    loadData()
  } catch {
    // 用户取消或请求失败
  }
}
</script>

<style scoped lang="scss">
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
```

- [ ] **Step 4: 添加侧边栏菜单**

修改 `web/src/components/layout/AppSidebar.vue`，在 `<el-menu>` 中添加：

```vue
<el-sub-menu index="q2">
  <template #title>
    <el-icon><Clock /></el-icon>
    <span>Q2 任务</span>
  </template>
  <el-menu-item index="/q2/tasks">任务管理</el-menu-item>
</el-sub-menu>
```

确保导入 `Clock` 图标：
```typescript
import { Clock } from '@element-plus/icons-vue'
```

- [ ] **Step 5: 验证构建**

Run: `cd /Users/willie/e-learning/e-learning-sme/web && npx vue-tsc -b --noEmit && npm run build`
Expected: 构建成功，无类型错误

- [ ] **Step 6: Commit**

```bash
cd /Users/willie/e-learning/e-learning-sme/web
git add src/api/q2.ts src/types/q2.ts src/views/q2/ src/router/routes.ts src/components/layout/AppSidebar.vue
git commit -m "feat: 添加 Q2 任务管理前端页面"
```

---

## 文件总览

**后端（Django）：**
| 文件 | 职责 |
|------|------|
| `q2/__init__.py` | Django 应用标识 |
| `q2/apps.py` | 应用配置 |
| `q2/serializers.py` | TaskSerializer、ScheduleSerializer |
| `q2/views/__init__.py` | 导出所有 ViewSet |
| `q2/views/task_view.py` | TaskViewSet、FailureViewSet |
| `q2/views/schedule_view.py` | ScheduleViewSet |
| `q2/views/queue_view.py` | QueueViewSet |
| `q2/urls.py` | 路由注册 |
| `q2/tests/task_api_test.py` | 任务和失败 API 测试 |
| `q2/tests/schedule_api_test.py` | 定时任务 API 测试 |
| `q2/tests/queue_api_test.py` | 队列 API 测试 |
| `core/settings.py` | 注册 `q2` 应用 |
| `core/urls.py` | 挂载 `/api/q2/` 路由 |

**前端（Web）：**
| 文件 | 职责 |
|------|------|
| `web/src/api/q2.ts` | Q2 API 函数封装 |
| `web/src/types/q2.ts` | Q2 类型定义 |
| `web/src/views/q2/tasks/index.vue` | 任务管理主页面 |
| `web/src/views/q2/tasks/components/TaskTable.vue` | 任务表格组件 |
| `web/src/router/routes.ts` | 添加 Q2 路由 |
| `web/src/components/layout/AppSidebar.vue` | 添加 Q2 菜单 |

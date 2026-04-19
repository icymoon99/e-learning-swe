from django.test import TestCase
from django.contrib.auth import get_user_model
from django_q.models import Schedule
from rest_framework.test import APIClient

User = get_user_model()


class ScheduleApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            is_superuser=False,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass123",
            is_superuser=True,
        )
        Schedule.objects.create(
            name="daily_report",
            func="myapp.tasks.daily_report",
            schedule_type=Schedule.HOURLY,
        )

    def test_list_schedules_requires_auth(self):
        resp = self.client.get("/api/q2/schedules/")
        self.assertEqual(resp.status_code, 401)

    def test_list_schedules(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/q2/schedules/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["content"]["count"], 1)

    def test_create_schedule_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/q2/schedules/", data={
            "name": "new_task",
            "func": "myapp.tasks.new_task",
            "schedule_type": "DAILY",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_create_schedule_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post("/api/q2/schedules/", data={
            "name": "weekly_cleanup",
            "func": "myapp.tasks.weekly_cleanup",
            "schedule_type": "DAILY",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Schedule.objects.count(), 2)

    def test_update_schedule_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        schedule = Schedule.objects.first()
        resp = self.client.put(f"/api/q2/schedules/{schedule.pk}/", data={
            "name": "updated_name",
            "func": schedule.func,
            "schedule_type": "DAILY",
        }, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_update_schedule_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        schedule = Schedule.objects.first()
        resp = self.client.put(f"/api/q2/schedules/{schedule.pk}/", data={
            "name": "updated_report",
            "func": schedule.func,
            "schedule_type": "DAILY",
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        schedule.refresh_from_db()
        self.assertEqual(schedule.name, "updated_report")

    def test_delete_schedule_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        schedule = Schedule.objects.first()
        resp = self.client.delete(f"/api/q2/schedules/{schedule.pk}/")
        self.assertEqual(resp.status_code, 403)

    def test_delete_schedule_by_admin(self):
        self.client.force_authenticate(user=self.admin)
        schedule = Schedule.objects.first()
        pk = schedule.pk
        resp = self.client.delete(f"/api/q2/schedules/{pk}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Schedule.objects.count(), 0)

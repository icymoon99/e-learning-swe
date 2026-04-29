"""沙箱工作目录隔离测试 — 数据迁移 + 各后端隔离行为"""

from django.test import TransactionTestCase
from sandbox.models import ElSandboxInstance
from sandbox.migrations.migrate_workdir import migrate_absolute_to_relative


class TestWorkDirDataMigration(TransactionTestCase):
    """测试 0003_migrate_workdir_to_relative 迁移

    使用 TransactionTestCase 因为迁移操作需要在事务外运行。
    """

    def test_absolute_work_dir_stripped_leading_slash(self):
        """System 类型的绝对路径 work_dir 和 root_path 应去掉前导 /"""
        instance = ElSandboxInstance.objects.create(
            name="with-abs", type="localsystem", status="active",
            metadata={"root_path": "/tmp/", "work_dir": "/workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertFalse(instance.metadata["work_dir"].startswith("/"))
        self.assertEqual(instance.metadata["work_dir"], "workspace")
        self.assertFalse(instance.metadata["root_path"].startswith("/"))

    def test_docker_work_dir_stripped(self):
        """Docker 类型的绝对路径 work_dir 应去掉前导 /"""
        instance = ElSandboxInstance.objects.create(
            name="docker-abs", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertEqual(instance.metadata["work_dir"], "workspace")

    def test_relative_paths_unchanged(self):
        """已经是相对路径的不应被修改"""
        instance = ElSandboxInstance.objects.create(
            name="already-relative", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        instance.refresh_from_db()
        self.assertEqual(instance.metadata["work_dir"], "workspace")
        self.assertEqual(instance.metadata["root_path"], "sandbox/")

    def test_migration_fails_on_empty_workdir(self):
        """work_dir 为空（去掉了 / 后）时应抛出 ValueError"""
        ElSandboxInstance.objects.create(
            name="empty-workdir", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/"},
        )
        with self.assertRaises(ValueError) as ctx:
            migrate_absolute_to_relative(ElSandboxInstance)
        self.assertIn("work_dir 为空", str(ctx.exception))

    def test_migration_fails_on_dotdot_path(self):
        """work_dir 包含 .. 时迁移应失败"""
        ElSandboxInstance.objects.create(
            name="dotdot", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "../../../etc"},
        )
        with self.assertRaises(ValueError) as ctx:
            migrate_absolute_to_relative(ElSandboxInstance)
        self.assertIn("work_dir 包含 ..", str(ctx.exception))

    def test_no_instance_left_with_absolute_path(self):
        """迁移后数据库中不应存在任何绝对路径"""
        ElSandboxInstance.objects.create(
            name="abs-1", type="localdocker", status="active",
            metadata={"image": "sandbox:latest", "work_dir": "/workspace"},
        )
        ElSandboxInstance.objects.create(
            name="abs-2", type="localsystem", status="active",
            metadata={"root_path": "/home/user/", "work_dir": "/tmp/work"},
        )
        ElSandboxInstance.objects.create(
            name="rel-1", type="localsystem", status="active",
            metadata={"root_path": "sandbox/", "work_dir": "workspace"},
        )

        migrate_absolute_to_relative(ElSandboxInstance)

        for inst in ElSandboxInstance.objects.all():
            if "work_dir" in inst.metadata:
                self.assertFalse(
                    inst.metadata["work_dir"].startswith("/"),
                    f"{inst.name} 仍有绝对路径 work_dir"
                )
            if inst.type in ("localsystem", "remotesystem"):
                if "root_path" in inst.metadata:
                    self.assertFalse(
                        inst.metadata["root_path"].startswith("/"),
                        f"{inst.name} 仍有绝对路径 root_path"
                    )

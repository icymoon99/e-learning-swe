"""数据迁移：将 ElSandboxInstance metadata 中的绝对路径转为相对路径"""

from django.db import migrations

from sandbox.migrations.migrate_workdir import migrate_absolute_to_relative


def _run_migration(apps, schema_editor):
    ElSandboxInstance = apps.get_model("sandbox", "ElSandboxInstance")
    migrate_absolute_to_relative(ElSandboxInstance)


class Migration(migrations.Migration):
    dependencies = [
        ("sandbox", "0002_remove_elsandboxinstance_root_path"),
    ]
    operations = [
        migrations.RunPython(
            _run_migration,
            migrations.RunPython.noop,
        ),
    ]

# This migration previously added a 'roles' field referencing system.role.
# The system.role model has been deleted, so this migration is now a no-op.
# The field was removed in migration 0003_remove_eluser_roles.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        # No-op: system.role model no longer exists
    ]

# This migration previously removed the 'roles' field.
# Since migration 0002 is now a no-op, this migration is also a no-op.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_eluser_roles'),
    ]

    operations = [
        # No-op: field was never added (migration 0002 is a no-op)
    ]

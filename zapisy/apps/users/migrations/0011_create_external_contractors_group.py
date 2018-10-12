from django.contrib.auth.models import Group
from django.db import models, migrations


EXTERNAL_CONTRACTORS_GROUP_NAME = 'external_contractors'


def apply_migration(apps, schema_editor):
    Group.objects.create(name=EXTERNAL_CONTRACTORS_GROUP_NAME)


def revert_migration(apps, schema_editor):
    Group.objects.filter(name=EXTERNAL_CONTRACTORS_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20180712_1227'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration)
    ]

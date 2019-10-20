"""
This migration creates a thesis board group;
users can then be added to this group using the admin interface.
"""

from django.db import migrations
from ..users import THESIS_BOARD_GROUP_NAME


def create_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).create(name=THESIS_BOARD_GROUP_NAME)


def remove_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    Group.objects.using(db_alias).filter(name=THESIS_BOARD_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('theses', '0002_create_system_settings'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group)
    ]

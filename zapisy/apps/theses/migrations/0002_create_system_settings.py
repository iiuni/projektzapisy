"""
This migration creates a single instance of models.ThesesSystemSettings;
this is to allow to edit the configuration via the admin interface,
without changing settings.py and restarting the app
"""

from django.db import migrations


DEFAULT_REQUIRED_THESIS_VOTES = 3


def create_thesis_settings(apps, schema_editor):
    ThesesSystemSettings = apps.get_model("theses", "ThesesSystemSettings")
    db_alias = schema_editor.connection.alias
    ThesesSystemSettings.objects.using(db_alias).create(
        num_required_votes=DEFAULT_REQUIRED_THESIS_VOTES
    )


def remove_system_settings(apps, schema_editor):
    ThesesSystemSettings = apps.get_model("theses", "ThesesSystemSettings")
    db_alias = schema_editor.connection.alias
    ThesesSystemSettings.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('theses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_thesis_settings, remove_system_settings)
    ]

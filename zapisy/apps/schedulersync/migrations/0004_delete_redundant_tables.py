# This migration is for removing redundant tables from database
# It has nothing to do with schedulersync app and its models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedulersync', '0003_coursemap_employeemap'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS south_migrationhistory;'),
        migrations.RunSQL('DROP TABLE IF EXISTS auth_message;'),
    ]

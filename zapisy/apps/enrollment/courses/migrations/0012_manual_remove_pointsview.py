"""Removes all the views, functions and triggers computing Points for courses in
database.
"""

from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0011_manual_remove_openingtimesview'),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW IF EXISTS student_course_points_unmaterialized;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_entity_update_points_dt() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_entity_update_points_it() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_entity_update_points_ut() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_points_dt() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_points_it() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_points_ut() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS points_refresh_for_entity(integer);"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS points_refresh_for_student(integer);"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS execute(text);"),
    ]

"""Removes all the views, functions and triggers computing the Opening Times in 
database.
"""

from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0010_auto_20180804_2031'),
        ('users', '0012_auto_20180804_2031'),
        ('records', '0004_auto_20180804_2031'),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW IF EXISTS users_openingtimesview_unmaterialized;"),
        migrations.RunSQL("DROP VIEW IF EXISTS users_minutes_bonus_view;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS users_openingtimesview_refresh_for_semester(integer);"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS users_openingtimesview_refresh_for_student(integer);"),
        migrations.RunSQL("DROP TRIGGER IF EXISTS change_semester_update_points_delete ON courses_semester;"),
        migrations.RunSQL("DROP TRIGGER IF EXISTS change_semester_update_points_insert ON courses_semester;"),
        migrations.RunSQL("DROP TRIGGER IF EXISTS change_semester_update_points_update ON courses_semester;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_semester_update_user_opening_times_dt() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_semester_update_user_opening_times_it() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_semester_update_user_opening_times_ut() CASCADE;"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_user_opening_times_dt();"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_user_opening_times_it();"),
        migrations.RunSQL("DROP FUNCTION IF EXISTS change_student_update_user_opening_times_ut();"),
    ]

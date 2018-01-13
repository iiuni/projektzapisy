# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='type_of_points',
            field=models.ForeignKey(
                verbose_name=b'rodzaj punkt\xc3\xb3w',
                to='courses.PointTypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openingtimesview',
            name='course',
            field=models.ForeignKey(
                to='courses.Course'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='openingtimesview',
            name='semester',
            field=models.ForeignKey(
                to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(
                related_name='employee',
                verbose_name=b'U\xc5\xbcytkownik',
                to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]

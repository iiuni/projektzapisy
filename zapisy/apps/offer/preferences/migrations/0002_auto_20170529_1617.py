# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0001_initial'),
        ('users', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preference',
            name='employee',
            field=models.ForeignKey(verbose_name=b'pracownik', to='users.Employee', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='preference',
            name='proposal',
            field=models.ForeignKey(verbose_name=b'propozycja', to='courses.CourseEntity', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]

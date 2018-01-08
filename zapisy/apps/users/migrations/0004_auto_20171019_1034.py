# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170601_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openingtimesview',
            name='student',
            field=models.OneToOneField(related_name='opening_times', primary_key=True, serialize=False, to='users.Student'),
            preserve_default=True,
        ),
    ]

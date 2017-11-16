# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('records', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='group',
            field=models.ForeignKey(verbose_name=b'grupa', to='courses.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='record',
            name='student',
            field=models.ForeignKey(related_name='records', verbose_name=b'student', to='users.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='queue',
            name='group',
            field=models.ForeignKey(verbose_name=b'grupa', to='courses.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='queue',
            name='student',
            field=models.ForeignKey(related_name='queues', verbose_name=b'student', to='users.Student'),
            preserve_default=True,
        ),
    ]

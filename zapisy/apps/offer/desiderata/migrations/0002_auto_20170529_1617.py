# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('desiderata', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='desiderataother',
            name='employee',
            field=models.ForeignKey(verbose_name=b'prowadz\xc4\x85cy', to='users.Employee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='desiderataother',
            name='semester',
            field=models.ForeignKey(verbose_name=b'semestr', to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='desiderataother',
            unique_together=set([('employee', 'semester')]),
        ),
        migrations.AddField(
            model_name='desiderata',
            name='employee',
            field=models.ForeignKey(verbose_name=b'prowadz\xc4\x85cy', to='users.Employee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='desiderata',
            name='semester',
            field=models.ForeignKey(verbose_name=b'semestr', to='courses.Semester'),
            preserve_default=True,
        ),
    ]

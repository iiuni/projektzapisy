# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedescription',
            name='exam',
            field=models.BooleanField(default=False, verbose_name=b'egzamin'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='coursedescription',
            name='is_ready',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='courseentity',
            name='suggested_for_first_year',
            field=models.BooleanField(default=False, verbose_name=b'polecany dla pierwszego roku'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='semester',
            name='is_grade_active',
            field=models.BooleanField(default=False, verbose_name=b'Ocena aktywna'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='semester',
            name='visible',
            field=models.BooleanField(default=False, verbose_name=b'widoczny'),
            preserve_default=True,
        ),
    ]

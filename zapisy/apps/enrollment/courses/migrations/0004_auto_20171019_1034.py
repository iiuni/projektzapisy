# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_auto_20170606_1842'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='courseentity',
            options={
                'ordering': ['name_pl'],
                'verbose_name': 'Podstawa przedmiotu',
                'verbose_name_plural': 'Podstawy przedmiot\xf3w'},
        ),
    ]

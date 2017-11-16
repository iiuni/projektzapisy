# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20170529_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='visible',
            field=models.BooleanField(default=False, verbose_name='Wydarzenie jest publiczne'),
            preserve_default=True,
        ),
    ]

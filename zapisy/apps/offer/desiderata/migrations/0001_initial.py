# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Desiderata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.CharField(max_length=1, verbose_name=b'dzie\xc5\x84 tygodnia', choices=[(b'1', 'poniedzialek'), (b'2', 'wtorek'), (b'3', 'sroda'), (b'4', 'czwartek'), (b'5', 'piatek'), (b'6', 'sobota'), (b'7', 'niedziela')])),
                ('hour', models.IntegerField(verbose_name=b'godzina')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DesiderataOther',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(default=b'', max_length=200, verbose_name=b'uwagi')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DontSendEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50, verbose_name=b'adres')),
                ('when_added', models.DateTimeField(verbose_name=b'od kiedy')),
            ],
            options={
                'verbose_name': 'blokada',
                'verbose_name_plural': 'blokady',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50, verbose_name=b'odbiorca')),
                ('from_address', models.CharField(max_length=50, verbose_name=b'nadawca')),
                ('subject', models.CharField(max_length=100, verbose_name=b'temat')),
                ('message_body', models.TextField(verbose_name=b'tre\xc5\x9b\xc4\x87')),
                ('message_body_html', models.TextField(verbose_name=b'tre\xc5\x9b\xc4\x87 html', blank=True)),
                ('when_added', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'dodano')),
                ('priority', models.CharField(default=b'2', max_length=1, verbose_name=b'priorytet', choices=[(b'1', b'wysoki'), (b'2', b'\xc5\x9bredni'), (b'3', b'niski'), (b'4', b'odroczona')])),
            ],
            options={
                'verbose_name': 'wiadomo\u015b\u0107',
                'verbose_name_plural': 'wiadomo\u015bci',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50, verbose_name=b'odbiorca')),
                ('from_address', models.CharField(max_length=50, verbose_name=b'nadawca')),
                ('subject', models.CharField(max_length=100, verbose_name=b'temat')),
                ('message_body', models.TextField(verbose_name=b'tre\xc5\x9b\xc4\x87')),
                ('message_body_html', models.TextField(verbose_name=b'tre\xc5\x9b\xc4\x87 html', blank=True)),
                ('when_added', models.DateTimeField(verbose_name=b'dodano')),
                ('priority', models.CharField(max_length=1, verbose_name=b'priorytet', choices=[(b'1', b'wysoki'), (b'2', b'\xc5\x9bredni'), (b'3', b'niski'), (b'4', b'odroczona')])),
                ('when_attempted', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'czas pr\xc3\xb3by')),
                ('result', models.CharField(max_length=1, verbose_name=b'wynik', choices=[(b'1', b'sukces'), (b'2', b'nie wys\xc5\x82ane'), (b'3', b'niepowodzenie')])),
                ('log_message', models.TextField(verbose_name=b'wiadomo\xc5\x9b\xc4\x87')),
            ],
            options={
                'verbose_name': 'log',
                'verbose_name_plural': 'logi',
            },
            bases=(models.Model,),
        ),
    ]

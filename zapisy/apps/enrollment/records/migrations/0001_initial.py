# -*- coding: utf-8 -*-


from django.db import models, migrations
import apps.enrollment.records.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name=b'Czas do\xc5\x82\xc4\x85czenia do kolejki')),
                ('edited', models.DateTimeField(auto_now=True, verbose_name=b'Czas ostatniej zmiany')),
                ('priority', models.PositiveSmallIntegerField(default=1, verbose_name=b'priorytet', validators=[apps.enrollment.records.models.queue_priority])),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'kolejka',
                'verbose_name_plural': 'kolejki',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=1, verbose_name=b'status', choices=[(b'0', 'usuni\u0119ty'), (b'1', 'zapisany'), (b'2', 'przypi\u0119ty')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'utworzono')),
                ('edited', models.DateTimeField(auto_now=True, verbose_name=b'zmieniano')),
            ],
            options={
                'verbose_name': 'zapis',
                'verbose_name_plural': 'zapisy',
            },
            bases=(models.Model,),
        ),
    ]

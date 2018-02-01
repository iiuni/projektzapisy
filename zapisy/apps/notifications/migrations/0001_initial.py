# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreferences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50, verbose_name='typ', choices=[(b'send-news', 'Dodano nowy news'), (b'enrollment-limit', 'Podniesiono limit ECTS'), (b'vote-start', 'Rozpocz\u0119\u0142o si\u0119 g\u0142osowanie'), (b'grade-start', 'Rozpocz\u0119\u0142a si\u0119 ocena')])),
                ('value', models.BooleanField(default=True, verbose_name='warto\u015b\u0107')),
                ('user', models.ForeignKey(verbose_name='u\u017cytkownik', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'Ustawienie Notyfikacji',
                'verbose_name_plural': 'Ustawienia Notyfikacji',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notificationpreferences',
            unique_together=set([('user', 'type')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailChangeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verification_key', models.CharField(max_length=40)),
                ('email', models.EmailField(max_length=75)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(related_name='emailchangerequest_user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'email change request',
                'verbose_name_plural': 'email change requests',
            },
        ),
    ]

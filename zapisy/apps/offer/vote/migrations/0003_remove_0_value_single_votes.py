# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def remove_0_value_single_votes(apps, schema_editor):
    SingleVote = apps.get_model('vote', 'SingleVote')
    SingleVote.objects.filter(value=0, correction=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0002_auto_20180525_0559'),
    ]

    operations = [
        migrations.RunPython(remove_0_value_single_votes),
    ]

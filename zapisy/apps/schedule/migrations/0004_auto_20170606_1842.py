# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_auto_20170601_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventmoderationmessage',
            options={'ordering': ['created'], 'get_latest_by': 'created', 'verbose_name': 'wiadomo\\u015b\\u0107 wydarzenia', 'verbose_name_plural': 'wiadomo\\u015bci wydarzenia'},
        ),
    ]

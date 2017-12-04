# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0003_auto_20170601_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoicequestionanswer',
            name='options',
            field=models.ManyToManyField(to='poll.Option', verbose_name=b'odpowiedzi', blank=True),
        ),
    ]

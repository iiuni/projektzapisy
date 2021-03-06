# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-25 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20171112_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('0', 'Do rozpatrzenia'), ('1', 'Zaakceptowane'), ('2', 'Odrzucone')], default='0', max_length=1, verbose_name='Stan'),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('0', 'Egzamin'), ('1', 'Kolokwium'), ('2', 'Wydarzenie'), ('3', 'Zajęcia'), ('4', 'Inne')], max_length=1, verbose_name='Typ'),
        ),
        migrations.AlterField(
            model_name='specialreservation',
            name='dayOfWeek',
            field=models.CharField(choices=[('1', 'poniedziałek'), ('2', 'wtorek'), ('3', 'środa'), ('4', 'czwartek'), ('5', 'piątek'), ('6', 'sobota'), ('7', 'niedziela')], max_length=1, verbose_name='dzień tygodnia'),
        ),
        migrations.AlterField(
            model_name='specialreservation',
            name='end_time',
            field=models.TimeField(verbose_name='zakończenie'),
        ),
        migrations.AlterField(
            model_name='specialreservation',
            name='start_time',
            field=models.TimeField(verbose_name='rozpoczęcie'),
        ),
    ]

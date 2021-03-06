# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-25 05:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singlevote',
            name='correction',
            field=models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, verbose_name='korekta'),
        ),
        migrations.AlterField(
            model_name='singlevote',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.CourseEntity', verbose_name='podstawa'),
        ),
        migrations.AlterField(
            model_name='singlevote',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vote.SystemState', verbose_name='ustawienia głosowania'),
        ),
        migrations.AlterField(
            model_name='singlevote',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Student', verbose_name='głosujący'),
        ),
        migrations.AlterField(
            model_name='singlevote',
            name='value',
            field=models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3')], default=0, verbose_name='punkty'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='max_points',
            field=models.IntegerField(default=50, verbose_name='Maksimum punktów na przedmioty'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='max_vote',
            field=models.IntegerField(default=3, verbose_name='Maksymalna wartość głosu'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='semester_summer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='summer_votes', to='courses.Semester', verbose_name='Semestr letni'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='semester_winter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='winter_votes', to='courses.Semester', verbose_name='Semestr zimowy'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='summer_correction_beg',
            field=models.DateField(default=datetime.date(2016, 1, 1), verbose_name='Początek korekty letniej'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='summer_correction_end',
            field=models.DateField(default=datetime.date(2016, 7, 31), verbose_name='Koniec korekty letniej'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='vote_beg',
            field=models.DateField(default=datetime.date(2016, 6, 10), verbose_name='Początek głosowania'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='vote_end',
            field=models.DateField(default=datetime.date(2016, 7, 10), verbose_name='Koniec głosowania'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='winter_correction_beg',
            field=models.DateField(default=datetime.date(2016, 1, 1), verbose_name='Początek korekty zimowej'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='winter_correction_end',
            field=models.DateField(default=datetime.date(2016, 7, 31), verbose_name='Koniec korekty zimowej'),
        ),
        migrations.AlterField(
            model_name='systemstate',
            name='year',
            field=models.IntegerField(default=2018, verbose_name='Rok akademicki'),
        ),
    ]

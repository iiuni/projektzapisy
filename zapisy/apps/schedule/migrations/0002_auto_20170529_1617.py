# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='room',
            field=models.ForeignKey(related_name='event_terms', verbose_name='Sala', blank=True, to='courses.Classroom', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='specialreservation',
            name='classroom',
            field=models.ForeignKey(to='courses.Classroom'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='specialreservation',
            name='semester',
            field=models.ForeignKey(to='courses.Semester'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventmoderationmessage',
            name='author',
            field=models.ForeignKey(verbose_name='Autor', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventmoderationmessage',
            name='event',
            field=models.ForeignKey(verbose_name='Wydarzenie', to='schedule.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventmessage',
            name='author',
            field=models.ForeignKey(verbose_name='Autor', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventmessage',
            name='event',
            field=models.ForeignKey(verbose_name='Wydarzenie', to='schedule.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='author',
            field=models.ForeignKey(verbose_name='Tw\xf3rca', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='course',
            field=models.ForeignKey(blank=True, to='courses.Course', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(blank=True, to='courses.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='interested',
            field=models.ManyToManyField(related_name='interested_events', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='reservation',
            field=models.ForeignKey(blank=True, to='schedule.SpecialReservation', null=True),
            preserve_default=True,
        ),
    ]

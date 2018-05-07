from django.db import models


class TermSyncData(models.Model):
    """Stores the group numbers for the scheduler IDs so the importer can detect changes"""
    term = models.ForeignKey('courses.Term', verbose_name='termin')
    scheduler_id = models.PositiveIntegerField(null=True,
                                               verbose_name='id grupy w schedulerze')

    class Meta:
        verbose_name = 'Obiekt synchronizacji terminów grup'
        verbose_name_plural = 'Obiekty synchronizacji terminów grup'
        app_label = 'schedulersync'

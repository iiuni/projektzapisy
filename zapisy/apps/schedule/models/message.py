from django.contrib.auth.models import User
from django.db import models

from apps.schedule.models.event import Event


class EventModerationMessage(models.Model):
    author = models.ForeignKey(User, verbose_name='Autor', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, verbose_name='Wydarzenie', on_delete=models.CASCADE)
    message = models.TextField(verbose_name='Wiadomość')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'schedule'
        get_latest_by = 'created'
        ordering = ['created']
        verbose_name = 'wiadomość wydarzenia'
        verbose_name_plural = 'wiadomości wydarzenia'

    @classmethod
    def get_event_messages(cls, event):
        """Get list of EventMessages for event.

        @param event: Event object
        @return: list of EventModerationMessage
        """
        return cls.objects.filter(event=event).select_related('author')


class Message(models.Model):
    author = models.ForeignKey(User, verbose_name='Autor', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, verbose_name='Wydarzenie', on_delete=models.CASCADE)
    message = models.TextField(verbose_name='Wiadomość')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'schedule'
        get_latest_by = 'created'
        ordering = ['created']
        abstract = True

    @classmethod
    def get_event_messages(cls, event):
        """Get list of EventMessages for event.

        @param event: Event object
        @return: list of EventModerationMessage
        """
        return cls.objects.filter(event=event).select_related('author')


class EventMessage(Message):
    class Meta:
        app_label = 'schedule'
        verbose_name = 'wiadomość wydarzenia'
        verbose_name_plural = 'wiadomości wydarzenia'

# -*- coding: utf-8 -*-
from django.db import models


class EventModerationMessage(models.Model): #why two classes of the same name?
    from apps.schedule.models import Event
    from django.contrib.auth.models import User

    author = models.ForeignKey(User, verbose_name='Autor')
    event = models.ForeignKey(Event, verbose_name='Wydarzenie')
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
        """

        Get list of EventMessages for event

        @param event: Event object
        @return: list of EventModerationMessage
        """

        return cls.objects.filter(event=event).select_related('author')


class Message(models.Model):
    from apps.schedule.models import Event
    from django.contrib.auth.models import User

    author = models.ForeignKey(User, verbose_name='Autor')
    event = models.ForeignKey(Event, verbose_name='Wydarzenie')
    message = models.TextField(verbose_name='Wiadomość')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'schedule'
        get_latest_by = 'created'
        ordering = ['created']
        abstract = True

    @classmethod
    def get_event_messages(cls, event):
        """

        Get list of EventMessages for event

        @param event: Event object
        @return: list of EventModerationMessage
        """

        return cls.objects.filter(event=event).select_related('author')


class EventMessage(Message):

    class Meta:
        app_label = 'schedule'
        verbose_name = 'wiadomość wydarzenia'
        verbose_name_plural = 'wiadomości wydarzenia'

    def save(self, *args, **kwargs):
        super(EventMessage, self).save(*args, **kwargs)

#
#        render_and_send_email(u'Nowa wiadomość w wydarzeniu',
#                               u'schedule/emails/new_message.txt',
#                               u'schedule/emails/new_message.html',
#                               {'event': self.event},
#                               self.event.get_followers()
#        )

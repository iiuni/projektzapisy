from typing import List

from django.db import models
from django.contrib.auth.models import User

from apps.enrollment.records.models import Record, RecordStatus
from apps.users.models import Student


class NotificationPreferencesStudent(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    pulled_from_queue = models.BooleanField(default=True, verbose_name='Zapisanie Cię do grupy')
    not_pulled_from_queue = models.BooleanField(default=True, verbose_name='Niepowodzenie wciągnięcia Cię do grupy')
    added_new_group = models.BooleanField(default=True, verbose_name='Dodanie nowej grupy przedmiotu, na który jesteś '
                                                                     'zapisany/a')
    teacher_has_been_changed_enrolled = models.BooleanField(default=True, verbose_name='Zmiana prowadzącego grupy, '
                                                                                       'do której jesteś zapisany/a')
    teacher_has_been_changed_queued = models.BooleanField(default=True, verbose_name='Zmiana prowadzącego grupy, '
                                                                                     'do której czekasz w kolejce')
    news_has_been_added = models.BooleanField(default=True, verbose_name='Nowa wiadomość w Aktualnościach')


class NotificationPreferencesTeacher(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    assigned_to_new_group_as_teacher = models.BooleanField(default=True, verbose_name='Przydzielenie do grupy')
    news_has_been_added = models.BooleanField(default=True, verbose_name='Nowa wiadomość w Aktualnościach')

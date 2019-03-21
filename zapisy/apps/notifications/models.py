from typing import List

from django.db import models
from django.contrib.auth.models import User

from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record


def get_all_users_in_course_groups(course_groups: List[Group]):
    #queues = Queue.objects.filter(group__in=course_groups, deleted=False).select_related(
    #    'student', 'student__user')
    records = Record.objects.filter(group__in=course_groups, status=1).select_related(
        'student', 'student__user')

    return {element.student.user for element in records}

def get_all_students():
    records = User.objects.all()

    return { element for element in records }


class NotificationPreferencesStudent(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    pulled_from_queue = models.BooleanField(default=True, verbose_name='Wciągnięcie do grupy')
    not_pulled_from_queue = models.BooleanField(default=True, verbose_name='Anulowanie wciągnięcia do grupy')
    added_new_group = models.BooleanField(default=True, verbose_name='Dodanie nowej grupy przedmiotu, na który jesteś '
                                                                     'zapisany')
    teacher_has_been_changed = models.BooleanField(default=True, verbose_name='Zmiana prowadzącego grupy z przedmiotu, '
                                                                              'na który jesteś zapisany')
    news_has_been_added = models.BooleanField(default=True, verbose_name='Powiadomienie o nowej wiadomości w '
                                                                                'Aktualnościach')


class NotificationPreferencesTeacher(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    assigned_to_new_group_as_teacher = models.BooleanField(default=True, verbose_name='Przydzielenie do grupy')

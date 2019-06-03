from typing import List

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record, RecordStatus
from apps.users.models import Student


def get_all_users_in_course_groups(course_groups: List[Group]) -> set:
    records = Record.objects.filter(group__in=course_groups, status=1).select_related(
        'student', 'student__user')

    return {element.student.user for element in records}


def get_all_users_from_group(group: Group) -> set:
    records = Record.objects.filter(Q(group=group) & (Q(status=RecordStatus.QUEUED) | Q(status=RecordStatus.ENROLLED))).select_related('student', 'student__user')

    return {element.student.user for element in records}


def get_queued_users_from_group(group: Group) -> set:
    records = Record.objects.filter(group=group, status=RecordStatus.QUEUED).select_related('student', 'student__user')

    return {element.student.user for element in records}


def get_enrolled_users_from_group(group: Group) -> set:
    records = Record.objects.filter(group=group, status=RecordStatus.ENROLLED).select_related('student', 'student__user')

    return {element.student.user for element in records}


def get_all_users() -> set:
    records = User.objects.all()

    return {element for element in records}


def get_all_students() -> set:
    students = Student.objects.all()

    return {element.user for element in students}


class NotificationPreferencesStudent(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    #pulled_from_queue = models.BooleanField(default=True, verbose_name='Wciągnięcie do grupy')
    #not_pulled_from_queue = models.BooleanField(default=True, verbose_name='Anulowanie wciągnięcia do grupy')
    student_has_been_put_into_the_queue = models.BooleanField(default=True, verbose_name='Wciągniecie Cię do kolejki')
    student_has_been_enrolled = models.BooleanField(default=True, verbose_name='Zapisanie Cię do grupy')
    added_new_group = models.BooleanField(default=True, verbose_name='Dodanie nowej grupy przedmiotu, na który jesteś '
                                                                     'zapisany/a')
    teacher_has_been_changed_enrolled = models.BooleanField(default=True, verbose_name='Zmiana prowadzącego grupy, '
                                                                                       'do której jesteś zapisany/a')
    teacher_has_been_changed_queued = models.BooleanField(default=True, verbose_name='Zmiana prowadzącego grupy, '
                                                                                     'do której czekasz w kolejce')
    terms_have_been_changed_enrolled = models.BooleanField(default=True, verbose_name='Zmiana terminu grupy, '
                                                                                      'do której jesteś zapisany/a')
    terms_have_been_changed_queued = models.BooleanField(default=True, verbose_name='Zmiana terminu grupy, '
                                                                                      'do której czekasz w kolejce')
    news_has_been_added = models.BooleanField(default=True, verbose_name='Powiadomienie o nowej wiadomości w Aktualnościach')


class NotificationPreferencesTeacher(models.Model):
    user = models.ForeignKey(User, verbose_name='użytkownik', on_delete=models.CASCADE)
    assigned_to_new_group_as_teacher = models.BooleanField(default=True, verbose_name='Przydzielenie do grupy')
    news_has_been_added = models.BooleanField(default=True, verbose_name='Powiadomienie o nowej wiadomości w Aktualnościach')

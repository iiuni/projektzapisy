# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import signals
from django.db.models import Count
from django.core.cache import cache as mcache
from django.db.models.query import QuerySet
from django.conf import settings
from apps.notifications.models import Notification
from django.core.urlresolvers import reverse

from course import *

import logging

backup_logger = logging.getLogger('project.backup')

# w przypadku edycji, poprawić też javascript: Fereol.Enrollment.CourseGroup.groupTypes
GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'),
                      ('5', 'ćwiczenio-pracownia'),
                      ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF'),
                      ('9', 'repetytorium'), ('10', 'projekt')]

GROUP_EXTRA_CHOICES = [('', ''),
                       ("pierwsze 7 tygodni", "pierwsze 7 tygodni"),
                       ("drugie 7 tygodni", "drugie 7 tygodni"),
                       ('grupa rezerwowa', 'grupa rezerwowa'),
                       ('grupa licencjacka', 'grupa licencjacka'),
                       ('grupa magisterska', 'grupa magisterska'),
                       ('grupa zaawansowana', 'grupa zaawansowana'),
                       ('zajecia na mat.', u'zajęcia na matematyce'),
                       (u'wykład okrojony', 'wykład okrojony'),
                       (u'grupa 1', 'grupa 1'),
                       (u'grupa 2', 'grupa 2'),
                       (u'grupa 3', 'grupa 3'),
                       (u'grupa 4', 'grupa 4'),
                       (u'grupa 5', 'grupa 5'),
                       (u'pracownia linuksowa', 'pracownia linuksowa'),
                       (u'grupa anglojęzyczna', 'grupa anglojęzyczna'),
                       (u'I rok', 'I rok'), (u'II rok', 'II rok'), (u'ISIM', 'ISIM')
                       ]


class StatisticManager(models.Manager):
    """
    Return all groups in semester with additional statistic information

    @param {Semester} semester
    @return Queryset of Group
    """

    def in_semester(self, semester):
        return self.get_queryset().filter(course__semester=semester)\
            .select_related('course', 'teacher', 'teacher__user', 'course__entity')\
            .order_by('course')\
            .extra(select={
                'queued': "SELECT COUNT(*) FROM records_queue rq WHERE"
                " rq.deleted = False AND rq.group_id = courses_group.id",
                'pinned': "SELECT COUNT(*) FROM records_record rr "
                "WHERE rr.status='2' AND rr.group_id = courses_group.id"})


class Group(models.Model):
    """group for course"""
    course = models.ForeignKey('Course', verbose_name='przedmiot', related_name='groups')
    teacher = models.ForeignKey('users.Employee', null=True, blank=True, verbose_name='prowadzący')
    type = models.CharField(max_length=2, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    limit = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    limit_zamawiane = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='miejsca dla zamawianych 2009',
        help_text='miejsca gwarantowane dla studentów zamawianych 2009')
    limit_zamawiane2012 = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='miejsca dla zamawianych 2012',
        help_text='miejsca gwarantowane dla studentów zamawianych 2012')
    limit_isim = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='miejsca dla ISIM',
        help_text='miejsca gwarantowane dla studentów isim')
    extra = models.CharField(
        max_length=20,
        choices=GROUP_EXTRA_CHOICES,
        verbose_name='dodatkowe informacje',
        default='',
        blank=True)
    export_usos = models.BooleanField(default=True, verbose_name='czy eksportować do usos?')

    # we are not using these
    #cache_enrolled     = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość zapisanych studentów')
    #cache_enrolled_zam = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość zapisanych studentów zamawianych')
    #cache_queued       = models.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Cache: ilość studentów w kolejce')

    enrolled = models.PositiveIntegerField(
        default=0, editable=False, verbose_name='liczba zapisanych studentów')
    enrolled_zam = models.PositiveIntegerField(
        default=0, editable=False, verbose_name='liczba zapisanych studentów zamawianych')
    enrolled_zam2012 = models.PositiveIntegerField(
        default=0, editable=False, verbose_name='liczba zapisanych studentów zamawianych')
    enrolled_isim = models.PositiveIntegerField(
        default=0, editable=False, verbose_name='liczba zapisanych studentów ISIM')
    queued = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name='liczba studentów w kolejce')

    disable_update_signal = False

    usos_nr = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=u'Nr grupy w usos',
        help_text='UWAGA! Nie edytuj tego pola sam!')

    objects = models.Manager()
    statistics = StatisticManager()

    def get_teacher_full_name(self):
        """return teacher's full name of current group"""
        if self.teacher is None:
            return u'(nieznany prowadzący)'
        else:
            return self.teacher.user.get_full_name()

    def get_all_terms(self):
        """return all terms of current group"""
        return self.term.all()

    def get_all_terms_for_export(self):
        """return all terms of current group"""
        from apps.schedule.models import Term
        return Term.objects.filter(event__group=self)

    def human_readable_type(self):
        types = {
            '1': 'Wykład',
            '9': 'Repetytorium',
            '2': 'Ćwiczenia',
            '3': 'Pracownia',
            '4': 'Ćwiczenia (poziom zaawansowany)',
            '5': 'Ćwiczenio-pracownia',
            '6': 'Seminarium',
            '7': 'Lektorat',
            '8': 'Zajęcia sportowe',
            '10': 'Projekt',
        }
        return types[self.type]

    def get_terms_as_string(self):
        return ",".join(map(lambda x: "%s %s-%s" % (x.get_dayOfWeek_display(),
                                                    x.start_time.hour, x.end_time.hour), self.term.all()))
    get_terms_as_string.short_description = 'Terminy zajęć'

    def remove_from_queued_counter(self, student):
        # @param student:
        #           Student object
        # decrease queued couter, after remove student from queue
        self.queued -= 1
        self.save()

    def add_to_queued_counter(self, student):
        # @param student:
        #           Student object
        # increade queued couter, after add student to queue

        self.queued += 1
        self.save()

    def remove_from_enrolled_counter(self, student):
        # @param student:
        #           Student object
        # decrease enrolled couter, after remove student from group

        self.enrolled -= 1
        if student.is_zamawiany():
            self.enrolled_zam -= 1
        if student.is_zamawiany2012():
            self.enrolled_zam2012 -= 1
        if student.isim:
            self.enrolled_isim -= 1

        self.save()

    def add_to_enrolled_counter(self, student):
        # @param student:
        #           Student object
        # increase enrolled counter, after adding student to group

        self.enrolled += 1
        if student.is_zamawiany():
            self.enrolled_zam += 1
        if student.is_zamawiany2012():
            self.enrolled_zam2012 += 1
        if student.isim:
            self.enrolled_isim += 1
        self.save()

    def remove_student(self, student, is_admin=False):
        #  Removes student from this group. If this is Lecture group remove from other too.
        #  Remove from
        #  @return (state, messages)
        #  state:
        #        Group.QuerySet - when student was removed from other groups too
        #        True - when everything is ok
        #        False - something bad e.g. student wasn't in this group
        #  messages:
        #        [Text] - text info about actions

        from apps.enrollment.records.models import Record, Queue
        from apps.enrollment.courses.models import Semester

        # admins are always allowed to remove students
        if not is_admin:
            semester = Semester.objects.get_next()

            if semester.is_closed():
                return False, [
                    u'Zapisy na ten semestr zostały zakończone. Nie możesz dokonywać zmian.']

            elif not semester.can_remove_record() and not self.has_student_in_queue(student):
                return False, [
                    u'Wypisy w tym semestrze zostały zakończone. Nie możesz wypisać się z grupy.']

        result = True
        if Record.objects.filter(
                student=student,
                group=self,
                status=Record.STATUS_ENROLLED).update(
                status=Record.STATUS_REMOVED) > 0:
            message = [u'Student wypisany z grupy']

            lecture_records = Record.objects.filter(
                student=student,
                status=Record.STATUS_ENROLLED,
                group__course=self.course,
                group__type=settings.LETURE_TYPE)
            if self.type == settings.LETURE_TYPE and len(lecture_records) == 0:
                result = self._remove_from_all_groups(student)
                message.append(u'Automatycznie wypisano również z pozostałych grup')

            self.remove_from_enrolled_counter(student)

            return result, message

        if Queue.objects.filter(
                student=student,
                group=self,
                deleted=False).update(
                deleted=True) > 0:
            self.remove_from_queued_counter(student)
            return result, [u'Usunięto z kolejki']

        return False, [u'Operacja niemożliwa']

    def _remove_from_other_groups(self, student):
        from apps.enrollment.records.models import Record
        from apps.enrollment.records.utils import run_rearanged

        result = None
        for record in Record.get_student_records_for_group_type(student, self):
            result = record.group
            record.student_remove(student)
            run_rearanged(None, result)

        return result or True

    def _remove_from_all_groups(self, student):
        from apps.enrollment.records.models import Record
        from apps.enrollment.records.utils import run_rearanged

        records = Record.get_student_records_for_course(student, self.course)
        for record in records:
            record.student_remove(student)
            run_rearanged(None, record.group)

        return records or True

    def _add_to_lecture(self, student):
        from apps.enrollment.records.models import Record
        groups = Group.objects.filter(type=settings.LETURE_TYPE, course=self.course)
        result = []
        for group in groups:
            __, created = Record.objects.get_or_create(
                student=student, group=group, status=Record.STATUS_ENROLLED)
            if created:
                result.append(u'Nastąpiło automatyczne dopisanie do grupy wykładowej')
                group.add_to_enrolled_counter(student)

        return result

    def add_student(self, student, return_group=False, commit=True):
        from apps.enrollment.records.models import Record

        result = True
        # REMOVE FROM OTHER GROUP

        if self.type != settings.LETURE_TYPE:
            result = self._remove_from_other_groups(student)

            self._add_to_lecture(student)

        r, created = Record.objects.get_or_create(
            student=student, group=self, status=Record.STATUS_ENROLLED)
        if created:
            self.add_to_enrolled_counter(student)

        if commit:
            self.save()

        if return_group:
            if isinstance(result, QuerySet):
                return result, [u'Student dopisany do grupy', u'Wypisano z poprzedniej grupy']
            else:
                return result, [u'Student dopisany do grupy']

        return result, [u'Student dopisany do grupy']

    def enroll_student(self, student):
        from apps.enrollment.courses.models import Semester
        from apps.enrollment.records.models import Record

        if Record.objects.filter(
                group=self,
                student=student,
                status=Record.STATUS_ENROLLED).count() > 0:
            return False, [u"Jesteś już w tej grupie"]

        if not self.course.is_opened_for_student(student):
            return False, [u"Zapisy na ten przedmiot są dla Ciebie zamknięte"]

        semester = Semester.objects.get_next()

        if semester.is_closed():
            return False, [u'Zapisy na ten semestr zostały zakończone. Nie możesz dokonywać zmian.']

        current_limit = semester.get_current_limit()

        if not student.get_points_with_course(self.course) <= current_limit:
            return False, [u'Przekroczono limit ' +
                           str(current_limit) + u' punktów. Zapis niemożliwy.']

        can_enroll, result = self.student_can_enroll(student)

        if can_enroll:
            enrolled, messages = self.add_student(student)
            result.extend(messages)
            return enrolled, result
        else:
            queued, messages = self._add_student_to_queue(student)
            result.extend(messages)
            return queued, result

    def student_can_enroll(self, student):

        if self.is_full_for_student(student):
            return False, [u'Brak wolnych miejsc w grupie']

        return True, []

    def _add_student_to_queue(self, student):
        from apps.enrollment.records.models import Queue
        __, created = Queue.objects.get_or_create(group=self, student=student, deleted=False)
        if created:
            self.add_to_queued_counter(student)
            return True, [u"Student został dopisany do kolejki"]

        else:
            return False, [u"Student znajdował się już w kolejce"]

    def rearanged(self):
        from apps.enrollment.records.models import Queue
        from apps.enrollment.courses.models import Semester

        queued = Queue.objects.filter(deleted=False,
                                      group=self).order_by('time').select_related('student')
        to_removed = []
        result = None
        semester = Semester.objects.get_next()
        if semester.is_closed():
            return result

        for q in queued:
            if self.is_full_for_student(
                    q.student) and not self.course.is_opened_for_student(
                    q.student):
                continue

            limit, __ = self.student_can_enroll(q.student)

            if not limit:
                pass
            else:
                current_limit = semester.get_current_limit()
                if q.student.get_points_with_course(self.course) <= current_limit:
                    result, messages = self.add_student(q.student, return_group=True)
                    total_queues = 0
                    for old in Queue.objects.filter(
                            deleted=False,
                            student=q.student,
                            priority__lte=q.priority,
                            group__course=self.course,
                            group__type=q.group.type):
                        old.deleted = True
                        old.save()
                        if old.group != self:
                            old.group.remove_from_queued_counter(q.student)
                        else:
                            self.remove_from_queued_counter(q.student)
                        total_queues += 1
                    if isinstance(result, Group):
                        Notification.send_notification(q.student.user,
                                                       'enrolled-again',
                                                       {'group': self,
                                                        'old_group': result,
                                                        'messages': messages,
                                                        'another_queues': total_queues - 1})
                    else:
                        Notification.send_notification(
                            q.student.user, 'enrolled', {
                                'group': self, 'messages': messages, 'another_queues': total_queues - 1})

                    break
                to_removed.append(q)

        for queue in to_removed:
            queue.deleted = True
            self.remove_from_queued_counter(queue.student)
            queue.save()
            Notification.send_notification(queue.student.user,
                                           'queue-remove',
                                           {'group': self,
                                            'reason': u'Zapis spowodowałby przekroczenie limitu ECTS'})

        return result

    def should_be_rearranged(self):
        return self.queued > 0

    def get_limit_for_normal_student(self):
        return self.limit - self.limit_zamawiane - self.limit_zamawiane2012

    def get_limit_for_zamawiane2009(self):
        return self.limit - self.limit_zamawiane2012

    def get_limit_for_zamawiane2012(self):
        return self.limit - self.limit_zamawiane

    def get_normal_enrolled(self):
        return self.enrolled - self.enrolled_zam - self.enrolled_zam2012

    def limit_non_zamawiane(self):
        return self.limit - self.limit_zamawiane - self.limit_zamawiane2012

    def limit_non_isim(self):
        return self.limit - self.limit_isim

    def is_full_for_student(self, student):
        if self.limit_isim > 0:
            if student.isim:
                return self.limit <= self.enrolled
            else:
                return self.limit - self.limit_isim <= self.enrolled - \
                    min(self.enrolled_isim, self.limit_isim)

        if student.is_zamawiany():

            return self.get_limit_for_zamawiane2009() <= self.enrolled - \
                min(self.limit_zamawiane2012, self.enrolled_zam2012)
        elif student.is_zamawiany2012():
            return self.get_limit_for_zamawiane2012() <= self.enrolled - min(self.enrolled_zam, self.limit_zamawiane)
        else:
            return self.get_limit_for_normal_student() <= self.enrolled - min(self.enrolled_zam2012,
                                                                              self.limit_zamawiane2012) - min(self.enrolled_zam, self.limit_zamawiane)

    @staticmethod
    def do_rearanged(group):
        regroup = group
        while isinstance(regroup, Group):
            regroup = regroup.rearanged()

    @staticmethod
    def get_groups_by_semester(semester):
        """ returns all groups in semester """
        return Group.objects.filter(course__semester=semester). \
            select_related('teacher', 'teacher__user', 'course',
                           'course__entity__type', 'course__entity', 'course__semester').all()

    @staticmethod
    def get_groups_by_semester_opt(semester):
        """ returns all groups in semester """
        return Group.objects.filter(course__semester=semester). \
            select_related('teacher', 'teacher__user', 'course',
                           'course__entity__type', 'course__entity', 'course__semester').all()

    def get_group_limit(self):
        """return maximal amount of participants"""
        return self.limit

    def get_count_of_enrolled(self, dont_use_cache=False):
        return self.enrolled

    def get_count_of_enrolled_zamawiane(self, dont_use_cache=False):
        return self.enrolled_zam

    def get_count_of_enrolled_zamawiane2012(self, dont_use_cache=False):
        return self.enrolled_zam2012

    def get_count_of_enrolled_non_zamawiane(self, dont_use_cache=False):
        result = self.enrolled
        if self.limit_zamawiane and self.limit_zamawiane > 0:
            result -= self.enrolled_zam
        if self.limit_zamawiane2012 and self.limit_zamawiane2012 > 0:
            result -= self.enrolled_zam2012
        if self.limit_isim and self.limit_isim > 0:
            result -= self.enrolled_isim
        return result

    def get_count_of_enrolled_non_isim(self, dont_use_cache=False):
        return self.enrolled - self.enrolled_isim

    def get_count_of_queued(self, dont_use_cache=False):
        return self.queued

    def course_slug(self):
        return self.course.slug

    @staticmethod
    def teacher_in_present(employees, semester):
        teachers = Group.objects.filter(
            course__semester=semester).distinct().values_list(
            'teacher__pk', flat=True)

        for employee in employees:
            employee.teacher = employee.pk in teachers

        return employees

    def has_student_in_queue(self, student):
        from apps.enrollment.records.models import Queue
        return Queue.objects.filter(student=student, group=self).count() != 0

    def serialize_for_json(self, enrolled, queued, pinned, queue_priorities,
                           student=None, employee=None):
        """ Dumps this group state to form readable by JavaScript """
        zamawiany = student and student.is_zamawiany()

        data = {
            'id': self.pk,
            'type': int(self.type),
            'course': self.course_id,

            'url': reverse('records-group', args=[self.pk]),
            'teacher_name': self.teacher and self.teacher.user.get_full_name()
            or 'nieznany prowadzący',
            'teacher_url': self.teacher and reverse('employee-profile', args=[self.teacher.user.id]) or '',

            'is_teacher': False if (employee is None or self.teacher is None)
            else self.teacher.id == employee.id,
            'is_enrolled': self.id in enrolled,
            'is_queued': self.id in queued,
            'is_pinned': self.id in pinned,

            'limit': self.limit,
            'unavailable_limit': 0 if zamawiany else self.limit_zamawiane,
            'enrolled_count': self.get_count_of_enrolled(),
            'unavailable_enrolled_count': 0 if zamawiany else
            min(self.get_count_of_enrolled_zamawiane(),
                self.limit_zamawiane),
            'queued_count': self.get_count_of_queued(),
            'queue_priority': queue_priorities.get(self.pk, -1)
        }

        return data

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'courses'

    @staticmethod
    def get_all_in_semester(semester):
        return Group.objects.filter(
            course__semester=semester). select_related(
            'course',
            'course__semester',
            'course__entity',
            'teacher',
            'teacher__user').order_by('course__entity__name')

    def __unicode__(self):
        return "%s: %s - %s" % (unicode(self.course.entity.get_short_name()),
                                unicode(self.get_type_display()),
                                unicode(self.get_teacher_full_name()))

    def long_print(self):
        return "%s: %s - %s" % (unicode(self.course.entity.name),
                                unicode(self.get_type_display()),
                                unicode(self.get_teacher_full_name()))

    def get_absolute_url(self):
        return reverse('records-group', args=[self.id])


def log_add_group(sender, instance, created, **kwargs):
    if Group.disable_update_signal:
        return
    if created:
        group = instance
        GROUP_TYPE_MAPPING = {'1': 'w', '2': 'c', '3': 'p',
                              '4': 'C', '5': 'r',
                              '6': 's', '7': 'l', '8': 'l',
                              '9': 'w', '10': 'p'}
        kod_grupy = group.id
        kod_przed_sem = group.course.id
        teacher_name_array = (group.teacher and group.teacher.user.get_full_name()
                              or u"Nieznany prowadzący").split(" ")
        kod_uz = teacher_name_array[0]
        if teacher_name_array[0] != teacher_name_array[-1]:
            kod_uz += " " + teacher_name_array[-1]
        max_osoby = group.limit
        rodzaj_zajec = GROUP_TYPE_MAPPING[group.type]
        zamawiane_bonus = group.limit_zamawiane
        message = '[06] group has been created <%s><%s><%s><%s><%s><%s>' % (
            kod_grupy, kod_przed_sem, kod_uz.encode('utf-8'), max_osoby, rodzaj_zajec, zamawiane_bonus)
        backup_logger.info(message)


def log_limits_change(sender, instance, **kwargs):
    if Group.disable_update_signal:
        return
    try:
        group = instance
        old_group = Group.objects.get(id=group.id)

        if group.limit != old_group.limit:
            backup_logger.info(
                '[04] limit of group <%s> has changed from <%s> to <%s>' %
                (group.id, old_group.limit, group.limit))
        if group.limit_zamawiane != old_group.limit_zamawiane:
            backup_logger.info(
                '[05] limit-zamawiane of group <%s> has changed from <%s> to <%s>' %
                (group.id, old_group.limit_zamawiane, group.limit_zamawiane))
    except Group.DoesNotExist:
        pass


def log_delete_group(sender, instance, **kwargs):
    backup_logger.info('[07] group <%s> has been deleted' % instance.id)

#signals.pre_save.connect(log_limits_change, sender=Group)
#signals.post_save.connect(log_add_group, sender=Group)
#signals.post_delete.connect(log_delete_group, sender=Group)


def recache(sender, **kwargs):
    if Group.disable_update_signal:
        return
    mcache.clear()


#signals.post_save.connect(recache, sender=Group)
#signals.post_delete.connect(recache, sender=Group)

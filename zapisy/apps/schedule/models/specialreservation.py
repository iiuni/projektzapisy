# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import ValidationError
from datetime import date, datetime
from apps.schedule.models import Event

import zapisy.common as common

from apps.enrollment.courses.models import Semester, Term as CourseTerm


class SpecialReservationQuerySet(models.query.QuerySet):
    def on_day_of_week(self, day_of_week):
        return self.filter(dayOfWeek=day_of_week)

    def this_semester(self):
        return self.filter(semester=Semester.get_current_semester())

    def any_semester(self, semester):
        return self.filter(semester=semester)

    def in_classroom(self, classroom):
        return self.filter(classroom=classroom)

    def in_classrooms(self, classrooms):
        return self.filter(classroom__in=classrooms)

    def between_hours(self, start_time, end_time):
        return self.filter(start_time__lt=end_time, end_time__gt=start_time)


class SpecialReservationManager(models.Manager):
    def get_query_set(self):
        return SpecialReservationQuerySet(self.model, using=self._db)

    def on_day_of_week(self, day_of_week):
        return self.get_query_set().on_day_of_week(day_of_week)

    def this_semester(self):
        return self.get_query_set().this_semester()

    def any_semester(self, semester):
        return self.get_query_set().any_semester(semester)

    def in_classroom(self, classroom):
        return self.get_query_set().in_classroom(classroom)

    def in_classrooms(self, classrooms):
        return self.get_query_set().in_classrooms(classrooms)

    def between_hours(self, start_time, end_time):
        return self.get_query_set().between_hours(start_time, end_time)


class SpecialReservation(models.Model):
    from apps.enrollment.courses.models import Semester, Term, Classroom

    semester = models.ForeignKey(Semester)
    title = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom)
    dayOfWeek = models.CharField(max_length=1,
                                 choices=common.DAYS_OF_WEEK,
                                 verbose_name='dzień tygodnia')
    start_time = models.TimeField(verbose_name='rozpoczęcie', blank=False)
    end_time = models.TimeField(verbose_name='zakończenie', blank=False)
    ignore_conflicts = False

    objects = SpecialReservationManager()

    @classmethod
    def get_reservations_for_semester(cls, semester, day=None, classrooms=None, start_time=None, end_time=None):
        """ A versatile function returning SpecialReservations. day is either datetime.date or string """

        query = cls.objects.any_semester(semester)

        if day:
            if isinstance(day, date):
                day_of_week = CourseTerm.get_day_of_week(day)
            else:
                day_of_week = day
            query = query.on_day_of_week(day_of_week)

        if classrooms:
            query = query.in_classrooms(classrooms)

        if start_time and end_time:
            query = query.between_hours(start_time, end_time)

        return query

    def validate_against_all_terms(self):

        course_terms = CourseTerm.get_terms_for_semester(semester=self.semester,
                                                         day=self.dayOfWeek,
                                                         classrooms=[self.classroom],
                                                         start_time=self.start_time,
                                                         end_time=self.end_time)

        from .term import Term
        candidate_days = self.semester.get_all_days_of_week(self.dayOfWeek, start_date=max(datetime.now().date(), self.semester.lectures_beginning))

        terms = Term.get_terms_for_dates(dates=candidate_days,
                                         classroom=self.classroom,
                                         start_time=self.start_time,
                                         end_time=self.end_time)
        msg_list = []

        if course_terms:
            for t in course_terms:
                msg_list.append(u'W tym samym czasie w tej sali odbywają się zajęcia: ' + t.group.course.name + ' ' + unicode(t))

        if terms:
            for t in terms:
                if t.event.reservation != self and t.event.type != Event.TYPE_CLASS:
                    msg_list.append( u'W tym samym czasie ta sala jest zarezerwowana (wydarzenie): ' + unicode(t.event) + ' ' + unicode(t))

        if len(msg_list)>0:
            raise ValidationError(message={'__all__': msg_list}, code='overlap')

    def clean(self):
        """
        Overloaded clean method. Checks for any conflicts between this SpecialReservation
        and other SpecialReservations, Terms of Events and Terms of Course Groups

        """
        if self.end_time <= self.start_time:
            raise ValidationError(
                message={'end_time': [u'Koniec rezerwacji musi natępować po początku']},
                code='invalid'
            )

        if not self.classroom.can_reserve:
            raise ValidationError(
                message={'classroom': [u'Ta sala nie jest przeznaczona do rezerwacji']},
                code='invalid'
            )

        if not self.ignore_conflicts:
            self.validate_against_all_terms()

        super(SpecialReservation, self).clean()

    class Meta:
        app_label = 'schedule'
        verbose_name = u'rezerwacja stała'
        verbose_name_plural = u'rezerwacje stałe'

    def create_event(self):
        from .term import Term
        from .event import Event

        Event.objects.filter(reservation=self).delete()

        semester = self.semester

        ev = Event()
        ev.title = self.title
        ev.description = u'Rezerwacja cykliczna - ' + self.title
        ev.reservation = self
        ev.type = Event.TYPE_GENERIC
        ev.visible = True
        ev.status = Event.STATUS_ACCEPTED
        ev.author_id = 1
        ev.save()

        term_days = semester.get_all_days_of_week(day_of_week=self.dayOfWeek, start_date=max(datetime.now().date(), semester.lectures_beginning))

        for day in term_days:
            term = Term()
            term.event = ev
            term.day = day
            term.start = self.start_time
            term.end = self.end_time
            term.room = self.classroom
            term.save()

    def save(self, *args, **kwargs):
        super(SpecialReservation, self).save(*args, **kwargs)
        self.create_event()

    def __unicode__(self):
        return u'%s: %s - %s %s - %s' % (self.semester, self.title, self.get_dayOfWeek_display(),
                                         self.start_time, self.end_time)

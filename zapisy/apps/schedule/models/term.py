# -*- coding: utf-8 -*-

import collections
import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import models
from django.db.models.query import EmptyQuerySet

from .event import Event
from .specialreservation import SpecialReservation
from apps.enrollment.courses.models import Classroom, Term as CourseTerm, Semester




class Term(models.Model):
    """
    Term representation
    """

    event = models.ForeignKey(Event, verbose_name='Wydarzenie')

    day = models.DateField(verbose_name='Dzień')

    start = models.TimeField(verbose_name='Początek')
    end = models.TimeField(verbose_name='Koniec')

    room = models.ForeignKey(to=Classroom, null=True, blank=True, verbose_name='Sala',
                             related_name='event_terms')
    place = models.CharField(max_length=255, null=True, blank=True, verbose_name='Miejsce')
    ignore_conflicts = False

    def validate_against_event_terms(self):
        assert(self.room is not None)
        terms = Term.get_terms_for_dates(dates=[self.day],
                                         classroom=self.room,
                                         start_time=self.start,
                                         end_time=self.end)

        if self.pk:
            terms = terms.exclude(pk=self.pk)

        if terms:
            raise ValidationError(
                message={'__all__': ['W tym samym czasie ta sala jest zarezerwowana: ' +
                                     str(terms[0].event) + ' (wydarzenie)']},
                code='overlap')

    def validate_against_course_terms(self):
        assert(self.room is not None)
        semester = Semester.get_semester(self.day)
        if not semester: return
        if semester.lectures_beginning <= self.day and self.day <= semester.lectures_ending:

            course_terms = CourseTerm.get_terms_for_semester(semester=semester,
                                                             day=self.day,
                                                             classrooms=[self.room],
                                                             start_time=self.start,
                                                             end_time=self.end)
            if course_terms:
                raise ValidationError(
                    message={'__all__': ['W tym samym czasie w tej sali odbywają się zajęcia: ' +
                                         course_terms[0].group.course.name + ' ' + str(course_terms[0])]},
                    code='overlap'
                )

    def clean(self):
        """
        Overloaded method from models.Model
        """
        if self.start >= self.end:
            raise ValidationError(
                message={'end': ['Koniec musi następować po początku']},
                code='overlap')

        if not self.room and not self.place:
            raise ValidationError(
                message={'room': ['Musisz wybrać salę lub miejsce zewnętrzne'],
                         'place': ['Musisz wybrać salę lub miejsce zewnętrzne']},
                code='invalid'
            )

        if self.room:
            if not self.room.can_reserve:
                raise ValidationError(
                    message={'room': ['Ta sala nie jest przeznaczona do rezerwacji']},
                    code='invalid'
                )

            if not self.ignore_conflicts:
                self.validate_against_event_terms()
                self.validate_against_course_terms()

        super(Term, self).clean()


    class Meta:
        app_label = 'schedule'
        get_latest_by = 'end'
        ordering = ['day', 'start', 'end']
        verbose_name = 'termin'
        verbose_name_plural = 'terminy'

    def get_conflicted(self):
        if not self.room:
            return Term.objects.none()

        # X < B AND A < Y

        terms = Term.objects.filter(Q(room=self.room), Q(day=self.day), Q(event__status=Event.STATUS_ACCEPTED),
                                    Q(start__lt=self.end), Q(end__gt=self.start)) \
            .select_related('event')

        if self.pk:
            terms = terms.exclude(pk=self.pk)
        return terms

    def pretty_print(self):
        """Verbose html info about term.

        Format: {start} - {end} {title_with_url} (author)
        """
        return '%s - %s <a href="%s">%s</a> (%s)' % (
            self.start, self.end, self.event.get_absolute_url(),
            self.event.title, self.event.author)

    def get_room(self):
        return self.room

    def get_day(self):
        return self.day

    @classmethod
    def get_exams(cls):
        """
        Get list of events with type 'exam'

        @return: Term QuerySet
        """
        return cls.objects.filter(event__type__in=['0', '1']).order_by('day', 'event__course__entity__name', 'room') \
            .select_related('event', 'room', 'event__course', 'event__course__entity', 'event__course__semester')

    @classmethod
    def get_terms_for_dates(cls, dates, classroom, start_time=None, end_time=None):
        """
        Gets terms in specified classroom on specified days

        :param end_time: datetime.time
        :param start_time: datetime.time
        :param classroom: enrollment.courses.models.Classroom
        :param dates: datetime.date list
        """
        if start_time is None:
            start_time = datetime.time(8)
        if end_time is None:
            end_time = datetime.time(21)

        terms = cls.objects.filter(day__in=dates,
                                   start__lt=end_time,
                                   end__gt=start_time,
                                   room=classroom,
                                   event__status=Event.STATUS_ACCEPTED).select_related('event')

        return terms

    @classmethod
    def prepare_conflict_dict(cls, start_time, end_time):
        """
        Head is top term for which next terms (if conflicted in terms of time) will be considered as conflicts.
        current_result stores conflicts for given current head
        @return OrderedDict[day][room][head|conflicted]
        """
        candidates = Term.objects.filter(day__gte=start_time, day__lte=end_time).order_by('day', 'room', 'start', 'end').select_related('room', 'event')
        conflicts = collections.OrderedDict()
        current_result = dict()
        head = None
        for term in candidates:
            if (head is not None and (term.day != head.day or term.room != head.room)) or head is None:
                if current_result and current_result['conflicted']:
                    if head.day not in conflicts:
                        conflicts[head.day] = dict()
                    if head.room not in conflicts[head.day]:
                        conflicts[head.day][head.room] = dict()
                        conflicts[head.day][head.room][head.pk] = dict()
                    conflicts[head.day][head.room][head.pk] = current_result
                head = term
                current_result = {}
                current_result['head'] = head
                current_result['conflicted'] = list()
            elif head.end >= term.end and term.start >= head.start: # conflict
                current_result['conflicted'].append(term)
        return conflicts

    def __unicode__(self):
        return '{0:s}: {1:s} - {2:s}'.format(str(self.day),
                                             str(self.start),
                                             str(self.end))

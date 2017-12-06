# -*- coding: utf-8 -*-
from datetime import time
from django.core.urlresolvers import reverse

from django.db import models
import json
from django.db.models import Q
from autoslug import AutoSlugField

floors = [(0, 'Parter'), (1, 'I piętro'), (2, 'II Piętro'), (3, 'III piętro')]
types = [(0, 'Sala wykładowa'), (1, 'Sala ćwiczeniowa'), (2, 'Pracownia komputerowa - Windows'), (3, 'Pracownia komputerowa - Linux')]



class Classroom( models.Model ):
    """classroom in institute"""
    type = models.IntegerField(choices=types, default=1, verbose_name='typ')
    description = models.TextField(null=True, blank=True, verbose_name='opis')
    number = models.CharField( max_length = 20, verbose_name = 'numer sali' )
    # we don't use ordering properly
    order = models.IntegerField(null=True, blank=True)
    building = models.CharField( max_length = 75, verbose_name = 'budynek', blank=True, default='' )
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')
    floor = models.IntegerField(choices=floors, null=True, blank=True)
    can_reserve = models.BooleanField(default=False)
    slug =  AutoSlugField(populate_from='number', unique_with='number')


    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'courses'
        ordering = ['floor', 'number']

    def get_absolute_url(self):
        try:
            return reverse('events:classroom', args=[self.slug])
        except:
            return reverse('events:classrooms')

    def __str__(self):
        return str(self.number) + ' ('+str(self.capacity)+')'

    @classmethod
    def get_by_number(cls, number):
        return cls.objects.get(number=number)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.objects.get(slug=slug)

    @classmethod
    def get_terms_in_day(cls, date, ajax=False):
        from apps.schedule.models import Term as EventTerm, SpecialReservation
        from apps.enrollment.courses.models import Semester, Term, Freeday, ChangedDay

        rooms = cls.get_in_institute(reservation=True)

        if not ajax:
            return rooms

        # build a dictionary

        result = {}

        for room in rooms:

            if room.number not in result:
                result[room.number] = {'id'       : room.id,
                                       'number'  : room.number,
                                       'capacity': room.capacity,
                                       'type': room.get_type_display(),
                                       'description': room.description,
                                       'title': room.number,
                                       'terms': []}

        # fill event terms

        terms = EventTerm.objects.filter(day=date, room__in=rooms, event__status='1').select_related('room', 'event')
        def make_dict(start_time,end_time,title):
            return {'begin': ':'.join(str(start_time).split(':')[:2]),
                    'end': ':'.join(str(end_time).split(':')[:2]),
                    'title': title}

        for term in terms:
            result[term.room.number]['terms'].append(make_dict(term.start, term.end, term.event.title))

        if not Freeday.is_free(date):

            # get weekday and semester

            weekday = ChangedDay.get_day_of_week(date)
            selected_semester = Semester.get_semester(date)

            if selected_semester is None:
                return

            if selected_semester.lectures_beginning > date or date > selected_semester.lectures_ending:
                return json.dumps(result)

            # get courses data

            course_terms = Term.objects.filter(dayOfWeek=weekday,
                                               group__course__semester=selected_semester)\
                .select_related('classroom', 'group').prefetch_related('classrooms')

            # fill courses data

            for course_term in course_terms:
                for classroom in course_term.classrooms.all():
                    if classroom not in rooms:
                        continue
                    result[classroom.number]['terms'].append(make_dict(course_term.start_time,
                                                                       course_term.end_time,
                                                                       course_term.group.course.name))
                if course_term.classroom is None:
                    continue
                result[course_term.classroom.number]['terms'].append(make_dict(course_term.start_time,
                                                                               course_term.end_time,
                                                                               course_term.group.course.name))
        return json.dumps(result)


    @classmethod
    def get_in_institute(cls, reservation=False):
        rooms = cls.objects.all()

        if reservation:
            rooms = rooms.filter(can_reserve=True).order_by('floor', 'number')

        return rooms

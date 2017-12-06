# -*- coding: utf-8 -*-

import django_filters
from apps.enrollment.courses.models import Semester
from apps.schedule.models import Event, Term

FILTER_TYPE_CHOICES = [('', '---------')] + Event.TYPES
FILTER_STATUS_CHOICES = [('', '---------')] + Event.STATUSES
class EventFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(choices=FILTER_TYPE_CHOICES, label='Typ')
    status = django_filters.ChoiceFilter(choices=FILTER_STATUS_CHOICES, label='Status')

    class Meta:
        model = Event
        fields = ['title', 'type', 'visible', 'status']


class ExamFilter(django_filters.FilterSet):
    class Meta:
        model = Term
        fields = ['event__course__semester']



    def __init__(self, data=None, *args, **kwargs):
        if not data:
            semester = Semester.get_current_semester()
            data = { 'event__course__semester': semester.id }

        super(ExamFilter, self).__init__(data, *args, **kwargs)

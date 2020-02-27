import django_filters
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.event import Event
from apps.schedule.models.term import Term

BOOLEAN_CHOICES = [(True, "Tak"),
                   (False, "Nie")]


class EventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title',
                                      lookup_expr='icontains')
    type = django_filters.ChoiceFilter(choices=Event.TYPES,
                                       label='Typ',
                                       empty_label="Dowolny")
    status = django_filters.ChoiceFilter(choices=Event.STATUSES,
                                         label='Status',
                                         empty_label="Dowolny")
    visible = django_filters.ChoiceFilter(choices=BOOLEAN_CHOICES,
                                          empty_label="Dowolne")

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
            data = {'event__course__semester': semester.id}

        super(ExamFilter, self).__init__(data, *args, **kwargs)

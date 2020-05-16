from collections import defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import HiddenInput
from django.forms.models import inlineformset_factory

from apps.enrollment.courses.models.classroom import Classroom, Floors
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.event import Event
from apps.schedule.models.message import EventMessage, EventModerationMessage
from apps.schedule.models.term import Term


class TermForm(forms.ModelForm):
    ignore_conflicts = forms.BooleanField(required=False, label="", widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(TermForm, self).clean()
        self.instance.ignore_conflicts = cleaned_data.get('ignore_conflicts')
        return cleaned_data

    class Meta:
        model = Term
        fields = '__all__'
        widgets = {
            'event': HiddenInput(),
            'day': HiddenInput(),
            'start': HiddenInput(),
            'end': HiddenInput(),
            'room': HiddenInput(),
            'place': HiddenInput()

        }


TermFormSet = inlineformset_factory(Event, Term, extra=0, form=TermForm)


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = ('status', 'author', 'created', 'edited', 'group', 'interested')

    def __init__(self, user, data=None, **kwargs):

        if data:
            data = deepcopy(data)
            if 'type' not in data:
                data['type'] = Event.TYPE_GENERIC

        super(EventForm, self).__init__(data, **kwargs)
        if not self.instance.pk:
            self.instance.author = user
        if user.employee:
            self.fields['type'].choices = Event.TYPES_FOR_TEACHER
        else:
            self.fields['type'].choices = Event.TYPES_FOR_STUDENT

        if not user.employee:
            self.fields['course'].queryset = CourseInstance.objects.none()
        else:
            semester = Semester.get_current_semester()

            previous_semester = Semester.get_semester(datetime.now().date() - timedelta(days=30))

            queryset = CourseInstance.objects.filter(semester__in=[semester, previous_semester]). \
                select_related('semester'). \
                order_by('semester')

            if not user.has_perm('schedule.manage_events'):
                queryset = CourseInstance.objects.filter(
                    groups__type='1',
                    groups__teacher=user.employee,
                    semester__in=[semester, previous_semester])

            self.fields['course'].queryset = queryset

        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['type'].widget.attrs.update({'class': 'form-control'})
        self.fields['course'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['visible'].widget.attrs.update({'checked': '', 'class': 'custom-control-input'})


class EventModerationMessageForm(forms.ModelForm):
    class Meta:
        model = EventModerationMessage
        fields = ('message', )


class EventMessageForm(forms.ModelForm):
    class Meta:
        model = EventMessage
        fields = ('message', )


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('status',)


class TableReportForm(forms.Form):
    """Form for generating table-based events report."""
    today = date.today().isoformat()
    beg_date = forms.DateField(
        label='Od:',
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'value': today}))
    end_date = forms.DateField(
        label='Do:',
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'value': today}))
    rooms = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classrooms = Classroom.objects.filter(can_reserve=True)
        by_floor = defaultdict(list)
        floor_names = dict(Floors)
        for r in classrooms:
            by_floor[floor_names[r.floor]].append((r.pk, r.number))
        self.fields['rooms'].choices = by_floor.items()


class DoorChartForm(forms.Form):
    """Form for generating door event charts."""
    today = date.today().isoformat()
    rooms = forms.MultipleChoiceField()
    week = forms.CharField(max_length=10, widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        classrooms = Classroom.objects.filter(can_reserve=True)
        by_floor = defaultdict(list)
        floor_names = dict(Floors)
        for r in classrooms:
            by_floor[floor_names[r.floor]].append((r.pk, r.number))
        self.fields['rooms'].choices = by_floor.items()

        semester = Semester.get_current_semester()
        next_sem = Semester.objects.get_next()
        weeks = [(week[0], f"{week[0]} - {week[1]}") for week in semester.get_all_weeks()]
        if semester != next_sem:
            weeks.insert(0, ('nextsem', f"Generuj z planu zajęć dla semestru '{next_sem}'"))
        weeks.insert(0, ('currsem', f"Generuj z planu zajęć dla semestru '{semester}'"))
        self.fields['week'].widget.choices = weeks


class ConflictsForm(forms.Form):
    today = date.today().isoformat()
    beg_date = forms.DateField(
        label='Od:',
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'value': today}))
    end_date = forms.DateField(
        label='Do:',
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'value': today}))

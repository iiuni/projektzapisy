from copy import deepcopy
from django import forms
from django.forms import HiddenInput
from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.event import Event
from apps.schedule.models.term import Term
from apps.schedule.models.message import EventModerationMessage, EventMessage
from apps.users.models import BaseUser
from django.contrib.admin.widgets import FilteredSelectMultiple

from django.forms.models import inlineformset_factory


from datetime import timedelta, datetime, date


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
        if BaseUser.is_employee(user):
            self.fields['type'].choices = Event.TYPES_FOR_TEACHER
        else:
            self.fields['type'].choices = Event.TYPES_FOR_STUDENT

        if not BaseUser.is_employee(user):
            self.fields['course'].queryset = Course.objects.none()
        else:
            semester = Semester.get_current_semester()

            previous_semester = Semester.get_semester(datetime.now().date() - timedelta(days=30))

            queryset = Course.objects.filter(semester__in=[semester, previous_semester]). \
                select_related('semester', 'entity'). \
                order_by('semester')

            if not user.has_perm('schedule.manage_events'):
                queryset = Course.objects.filter(groups__type='1',
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


class ReportForm(forms.Form):
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
    rooms = forms.MultipleChoiceField(widget=FilteredSelectMultiple("sale", is_stacked=False))


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

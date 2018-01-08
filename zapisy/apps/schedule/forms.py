# -*- coding: utf-8 -*-
from copy import deepcopy
from django import forms
from django.db.models.query import EmptyQuerySet
from django.forms import HiddenInput
from apps.enrollment.courses.models import Course, Semester
from apps.schedule.models import Event, Term, EventModerationMessage, EventMessage
from apps.users.models import BaseUser
from django.contrib.admin.widgets import FilteredSelectMultiple

from django.forms.models import inlineformset_factory


from datetime import timedelta, datetime


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

        self.fields['title'].widget.attrs.update({'class' : 'span7'})
        self.fields['type'].widget.attrs.update({'class' : 'span7'})
        self.fields['course'].widget.attrs.update({'class' : 'span7'})
        self.fields['description'].widget.attrs.update({'class' : 'span7'})
        self.fields['visible'].widget.attrs.update({'checked': ''})

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
    beg_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd', 'class':'datepicker'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd', 'class':'datepicker'}))
    rooms = forms.MultipleChoiceField(widget=FilteredSelectMultiple("sale", is_stacked=False))

class ConflictsForm(forms.Form):
    beg_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd', 'class':'datepicker'}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'yyyy-mm-dd', 'class':'datepicker'}))


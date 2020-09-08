from collections import defaultdict
from datetime import date, datetime, timedelta

from django import forms
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Row, Column, HTML, Div

from apps.enrollment.courses.models.classroom import Classroom, Floors
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.semester import Semester
from apps.schedule.models.event import Event
from apps.schedule.models.message import EventMessage, EventModerationMessage
from apps.schedule.models.term import Term


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        exclude = ["event", "ignore_conflicts"]

    day = forms.DateField(label="",
                          help_text="Wybierz termin, aby zobaczyć dostępne sale.",
                          widget=forms.TextInput(
                              attrs={
                                  'type': 'date',
                                  'class': 'form-day',
                                  'min': datetime.now().strftime("%Y-%m-%d"),
                                  'disabled': True
                              }))
    start = forms.TimeField(label="",
                            widget=forms.TextInput(attrs={
                                'type': 'time',
                                'class': 'form-time form-start',
                                'disabled': True
                            }))
    end = forms.TimeField(label="",
                          widget=forms.TextInput(attrs={
                              'type': 'time',
                              'class': 'form-time form-end',
                              'disabled': True
                          }))
    place = forms.CharField(label="",
                            help_text="Wybierz lokalizację poniżej.",
                            required=False,
                            widget=forms.TextInput(attrs={
                                'class': 'form-place m-0',
                                'readonly': True
                            }))
    room = forms.ModelChoiceField(queryset=Classroom.objects.all(),
                                  widget=forms.HiddenInput(attrs={'class': 'form-room'}),
                                  required=False)

    def __init__(self, user, *args, **kwargs):
        super(TermForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        if user.has_perm('schedule.manage_events'):
            self.instance.ignore_conflicts = True

        self.helper.layout = Layout(
            Div(Row(
                Column('day', css_class='col-2 mb-0'),
                Column('start', css_class='form-group col-2 mb-0'),
                Column('end', css_class='form-group col-2 mb-0'),
                Column('place', css_class='form-group col-3 mb-0'),
                Column(HTML(
                    '<button class="btn btn-primary edit-term-form mb-1"> Edytuj </button> '
                    '<button class="btn btn-danger delete-term-form mb-1">Usuń</button>'
                ),
                    css_class='col-3 mb-0'),
                css_class='form-row p-2'),
                'room',
                'id',
                Div('DELETE', css_class='d-none'),
                css_class="term-form d-none"))


# Number of extra term forms is kept in this variable, as it is send to the form
ExtraTermsNumber = 10
NewTermFormSet = inlineformset_factory(Event,
                                       Term,
                                       extra=ExtraTermsNumber,
                                       min_num=1,
                                       validate_min=True,
                                       form=TermForm,
                                       can_delete=True)

EditTermFormSet = inlineformset_factory(Event,
                                        Term,
                                        extra=ExtraTermsNumber,
                                        form=TermForm,
                                        can_delete=True)


class CustomVisibleCheckbox(Field):
    template = 'forms/custom_visible_checkbox.html'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('status', 'author', 'created', 'edited', 'group', 'interested')

    title = forms.CharField(label="Nazwa", required=False)
    description = forms.CharField(
        label="Opis",
        help_text="Opis wydarzenia widoczny jest dla wszystkich, jeśli wydarzenie jest publiczne;"
        " widoczny tylko dla rezerwującego i administratora sal, gdy wydarzenie jest prywatne.",
        widget=forms.Textarea)
    type = forms.ChoiceField(choices=Event.TYPES_FOR_STUDENT,
                             label="Rodzaj",
                             widget=forms.Select(attrs={'id': 'form-type'}))
    visible = forms.BooleanField(
        label="Wydarzenie widoczne dla wszystkich użytkowników systemu",
        widget=forms.CheckboxInput(attrs={'class': ""}),
        required=False,
        help_text="Wydarzenia niepubliczne widoczne są jedynie dla autorów i osób z uprawnieniami moderatora."
    )
    course = forms.ModelChoiceField(queryset=CourseInstance.objects.none(),
                                    label="Przedmiot",
                                    required=False)

    def __init__(self, user, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        if not self.instance.pk:
            self.instance.author = user

        if user.employee:
            self.fields['type'].choices = Event.TYPES_FOR_TEACHER

            semester = Semester.get_current_semester()

            previous_semester = Semester.get_semester(datetime.now().date() - timedelta(days=30))

            if not user.has_perm('schedule.manage_events'):
                queryset = CourseInstance.objects.filter(
                    groups__type='1',
                    groups__teacher=user.employee,
                    semester__in=[semester, previous_semester])
            else:
                queryset = CourseInstance.objects.filter(
                    semester__in=[semester, previous_semester]).select_related(
                        'semester').order_by('semester')

            self.fields['course'].queryset = queryset

        self.helper.layout = Layout(
            'type',
            Div('course', css_id="form-course"),
            Div(CustomVisibleCheckbox('visible'), css_class="d-none form-event"),
            Div('title', css_class='d-none form-event'),
            'description',
        )


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
        next_sem = Semester.get_upcoming_semester()
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

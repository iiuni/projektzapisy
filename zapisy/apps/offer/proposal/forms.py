import os
import inspect
from typing import Optional

from crispy_forms import helper, layout
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
import yaml

from apps.enrollment.courses.models.course import (CourseDescription, CourseEntity)
from apps.offer.proposal.models import Proposal, ProposalStatus, StudentWork, Syllabus


class ProposalForm(forms.ModelForm):
    ects = forms.IntegerField(label='ECTS')

    def __init__(self, *args, **kwargs):
        full_edit = kwargs.pop('full_edit', False)
        super(ProposalForm, self).__init__(*args, **kwargs)
        if not full_edit:
            self.fields['lectures'].widget.attrs['readonly'] = True
            self.fields['repetitions'].widget.attrs['readonly'] = True
            self.fields['exercises'].widget.attrs['readonly'] = True
            self.fields['laboratories'].widget.attrs['readonly'] = True
            self.fields['exercises_laboratiories'].widget.attrs['readonly'] = True
            self.fields['seminars'].widget.attrs['readonly'] = True
            self.fields['ects'].widget.attrs['readonly'] = True

        # allow editing status if proposal is accepted
        instance = kwargs.pop('instance', None)
        if instance is None:
            self.fields.pop('status')
        else:
            excluded_statuses = [CourseEntity.STATUS_PROPOSITION, CourseEntity.STATUS_FOR_REVIEW]
            if instance.status in excluded_statuses:
                self.fields.pop('status')
            else:
                self.fields['status'].choices = [
                    x for x in self.fields['status'].choices if x[0] not in excluded_statuses
                ]

    class Meta:
        fields = ('name', 'name_en', 'status', 'type', 'exam', 'english', 'semester', 'web_page',
                  'effects', 'repetitions', 'lectures', 'exercises', 'laboratories',
                  'exercises_laboratiories', 'seminars')
        model = CourseEntity
        widgets = {'effects': FilteredSelectMultiple("efekty kształcenia", is_stacked=False)}


class ProposalDescriptionForm(forms.ModelForm):

    class Meta:
        fields = ('description', 'requirements')
        model = CourseDescription
        widgets = {
            'description': forms.Textarea(attrs={'class': 'tinymce'}),
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }


class SyllabusForm(forms.ModelForm):

    class Meta:
        fields = ('requirements', 'studies_type', 'year', 'requirements', 'objectives',
                  'effects_txt', 'contents', 'learning_methods', 'literature', 'passing_form',
                  'exam_hours', 'tests_hours', 'project_presentation_hours')
        model = Syllabus
        widgets = {
            'learning_methods': FilteredSelectMultiple("Metody kształcenia", is_stacked=False)
        }


class SelectVotingForm(forms.Form):
    courses = forms.MultipleChoiceField(widget=FilteredSelectMultiple("courses", is_stacked=False))


class EditProposalForm(forms.ModelForm):
    """Form for editing a Proposal model.

    A CourseInformation object should only be modified by the regular users
    using this form. It will take care to keep the current instance of the
    course up to date with the proposal.
    """
    ects = forms.IntegerField(
        max_value=15,
        label="ECTS",
        required=False,
        disabled=True,
        help_text="To pole wypełni się samo na podstawie typu przedmiotu.")

    @staticmethod
    def status_transitions(current_status: Optional[ProposalStatus]):
        """Defines allowed status transitions.

        Initially an employee may only set the status to DRAFT or PROPOSAL.
        PROPOSAL is accepted by the head of teaching (who changes the status
        to IN_OFFER) or rejected (status is changed to
        CORRECTIONS_REQUIRED).

        If corrections are required, the employee may resubmit the proposal
        again by changing the status back to PROPOSAL.

        If the proposal is accepted (IN_OFFER) it can be put into the
        current offer voting (IN_VOTE), left for future semesters or
        archived (WITHDRAWN).
        """
        if current_status is None:
            return [
                ProposalStatus.DRAFT,
                ProposalStatus.PROPOSAL,
            ]
        current_status = ProposalStatus(int(current_status))
        if current_status == ProposalStatus.DRAFT:
            return [
                ProposalStatus.DRAFT,
                ProposalStatus.PROPOSAL,
            ]
        elif current_status == ProposalStatus.IN_OFFER:
            return [
                ProposalStatus.IN_OFFER,
                ProposalStatus.IN_VOTE,
                ProposalStatus.WITHDRAWN,
            ]
        elif current_status == ProposalStatus.CORRECTIONS_REQUIRED:
            return [
                ProposalStatus.PROPOSAL,
                ProposalStatus.CORRECTIONS_REQUIRED,
            ]
        else:
            return [current_status]

    def status_choices(self):
        def choices_pair(c: ProposalStatus):
            """Generates a tuple like `.choices()` but with single choice only.
            """
            return (c, c.display)

        current_status = None if not self.data else self.data.get('status')
        return map(choices_pair, self.status_transitions(current_status))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ProposalFormHelper()

        # Populate initial values from dictionary.
        for k, val in self.Meta.initial_values.items():
            if isinstance(val, str):
                val = inspect.cleandoc(val)
            self.fields[k].initial = val

        # Limits status choices available to the user.
        self.fields['status'].choices = self.status_choices()

    def clean_status(self):
        """Verifies that the status change does not violate allowed transitions.
        """
        status = self.cleaned_data.get('status')
        status = ProposalStatus(status)
        old_status = None if not self.instance else self.instance.status
        if old_status is not None:
            old_status = ProposalStatus(old_status)
        if status not in self.status_transitions(old_status):
            raise forms.ValidationError(
                f"Nie można przejść ze statusu {old_status.display} do {status.display}.")
        return status

    def clean(self):
        """Verifies the correctness of provided data.

        It checks that fields 'contents', 'objectives', and 'literature' are
        populated when proposal is submitted (with status PROPOSAL), as they are
        required then.
        """
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        if status is not None:
            status = ProposalStatus(status)
        if status == ProposalStatus.PROPOSAL:
            all_requirements_satisfied = True
            contents = cleaned_data.get('contents')
            if not contents:
                all_requirements_satisfied = False
                self.add_error(
                    'contents',
                    f"By móc ustawić status <u>{status.display}</u> trzeba wypełnić treści programowe.")
            objectives = cleaned_data.get('objectives')
            if not objectives:
                all_requirements_satisfied = False
                self.add_error(
                    'objectives',
                    f"By móc ustawić status <u>{status.display}</u> trzeba wypełnić cele przedmiotu.")
            literature = cleaned_data.get('literature')
            if not literature:
                all_requirements_satisfied = False
                self.add_error('literature',
                               f"By móc ustawić status <u>{status.display}</u> trzeba opisać literaturę.")
            if not all_requirements_satisfied:
                raise forms.ValidationError((
                    f"By móc ustawić status <u>{status.display}</u> trzeba opisać <em>Treści "
                    "programowe</em>, <em>Cele przedmiotu</em> i <em>Literaturę</em>."))

        return cleaned_data

    class Meta:
        model = Proposal
        fields = [
            'name',
            'name_en',
            'short_name',
            'language',
            'semester',
            'course_type',
            'has_exam',
            'recommended_for_first_year',
            'description',
            'hours_lecture',
            'hours_exercise',
            'hours_lab',
            'hours_exercise_lab',
            'hours_seminar',
            'hours_recap',
            'status',
            'teaching_methods',
            'preconditions',
            'objectives',
            'contents',
            'teaching_effects',
            'literature',
            'verification_methods',
            'passing_means',
            'student_labour',
        ]
        help_texts = {
            'name': "Nazwa powinna być w języku wykładowym.",
            'name_en': "Dla przedmiotów po angielsku powinna być taka sama jak nazwa.",
            'language': """Wszystkie pola należy wypełnić w języku wykładowym.
                Aby zmienić język istniejącego przedmiotu należy stworzyć nową
                propozycję.""",
            'short_name': "np. „JFiZO”, „AiSD” — nazwa do wyświetlania w planie zajęć.",
            'description': "Można formatować tekst używając Markdown.",
            'status': "Szkic można sobie zapisać na później.",
            'teaching_methods': """Wyliczyć lub krótko opisać, np.: wykład ·
                wykład interaktywny · prezentacja · live coding · dyskusja ·
                analiza tekstu · e-learning · rozwiązywanie zadań z
                komentowaniem · indywidualne/grupowe rozwiązywanie zadań ·
                indywidualny/zespołowy projekt programistyczny · samodzielna
                praca przy komputerze · ćwiczenia warsztatowe · zajęcia terenowe
                · studium przypadku · samodzielne wykonywanie zadań
                zawodowych""",
            'literature': """Wyliczyć 1-5 pozycji; jeśli dana pozycja nie jest
                wymagana w całości - określić które części/rozdziały.""",
            'verification_methods': """Podać sposoby pozwalające sprawdzić
                osiągnięcie wszystkich efektów kształcenia podanych powyżej, np.
                egzamin pisemny · kolokwium · prezentacja projektu · prezentacja
                rozwiązania zadania · opracowanie i przedstawienie prezentacji
                na zadany temat · napisanie programu komputerowego · realizacja
                zadań przy komputerze.""",
            'student_labour': """Wyliczyć rodzaje aktywności studenta i
                przybliżoną liczbę godzin. Suma godzin powinna wynosić około
                25 * liczba ECTS.""",
        }

        initial_values = {
            'hours_lecture': 30,
            'hours_exercise': 30,
            'hours_lab': 0,
            'hours_exercise_lab': 0,
            'hours_seminar': 0,
            'hours_recap': 0,
            'preconditions': """## Zrealizowane przedmioty:
                   *  \n
                ## Niezbędne kompetencje:
                   *  """,
            'student_labour': """## Zajęcia z udziałem nauczyciela:
                _dodatkowe względem programowych godzin zajęć, np. udział w
                egzaminie_
                  * udział w egzaminie **??**
                  * dodatkowe konsultacje w ramach potrzeb **??**
                ## Praca własna studenta:
                _np. rozwiązywanie zadań z list · przygotowanie do
                kolokwium/egzaminu · czytanie literatury · rozwiązywanie zadań
                programistycznych_
                  * przygotowywanie się do ćwiczeń (w tym czytanie materiałów
                    dodatkowych) **??**
                  * samodzielne rozwiązywanie zadań pracownianych i
                    projektowych **??**
                  * przygotowanie do egzaminu lub rozwiązywanie dodatkowych
                    zadań **??**""",
        }


class CustomCheckbox(layout.Field):
    """Renders Bootstrap 4 custom checkboxes.

    Inspired by
    https://simpleisbetterthancomplex.com/tutorial/2018/11/28/advanced-form-rendering-with-django-crispy-forms.html.
    """
    template = 'proposal/fields/custom_checkbox.html'


class Markdown(layout.Field):
    """Renders textarea with Markdown preview.

    For the editor to work, the bundle 'proposal-markdown-editor' must be
    included in the template.
    """
    template = 'proposal/fields/markdown.html'


class FormRow(layout.Div):
    """Represents Booststrap 4 form layout row."""
    css_class = 'form-row'


class Column(layout.Column):
    """Represents Bootstrap 4 layout column."""
    css_class = 'col-12 col-sm'


class ProposalFormHelper(helper.FormHelper):
    """Defines layout for the Proposal form.

    Fields here must be the same as in `EditProposalForm`.
    """
    layout = layout.Layout(
        layout.Fieldset(
            "Informacje podstawowe",
            FormRow(
                Column('name', css_class='col-md-8'),
                Column('language', css_class='col-md-4'),
            ),
            FormRow(
                Column('semester', css_class='col-md-4'),
                Column('course_type', css_class='col-md-4'),
                Column(
                    CustomCheckbox('has_exam'),
                    CustomCheckbox('recommended_for_first_year'),
                    css_class='col-md-4 px-4'),
                css_class='align-items-end',
            ),
            Markdown('description'),
            FormRow(
                Column('hours_lecture', css_class='col-md-2'),
                Column('hours_exercise', css_class='col-md-2'),
                Column('hours_lab', css_class='col-md-2'),
                Column('hours_exercise_lab', css_class='col-md-2'),
                Column('hours_seminar', css_class='col-md-2'),
                Column('hours_recap', css_class='col-md-2'),
                css_class='align-items-end',
            ), FormRow(
                Column('ects'),
                Column('status'),
            )),
        layout.Fieldset(
            "Informacje szczegółowe"
            # Fieldset collapse button.
            '<a class="btn btn-outline-secondary btn-sm ml-3" data-toggle="collapse" '
            'href="#proposal-details-fields" role="button" aria-expanded="false">'
            'Rozwiń/Zwiń</a>',
            layout.Div(
                'name_en',
                Markdown('teaching_methods'),
                Markdown('preconditions'),
                Markdown('objectives'),
                Markdown('contents'),
                Markdown('teaching_effects'),
                Markdown('literature'),
                Markdown('verification_methods'),
                Markdown('passing_means'),
                Markdown('student_labour'),
                css_class='collapse',
                css_id='proposal-details-fields',
            )),
        layout.Submit('submit', "Zapisz"),
    )

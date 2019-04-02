from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Column, Div, Layout, Row, Submit, Field, Fieldset)
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm

from apps.enrollment.courses.models.course import (CourseDescription,
                                                   CourseEntity)
from apps.offer.proposal.models import Proposal, StudentWork, Syllabus


class ProposalForm(ModelForm):
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
                    x for x in self.fields['status'].choices if x[0] not in excluded_statuses]

    class Meta:
        fields = (
            'name',
            'name_en',
            'status',
            'type',
            'exam',
            'english',
            'semester',
            'web_page',
            'effects',
            'repetitions',
            'lectures',
            'exercises',
            'laboratories',
            'exercises_laboratiories',
            'seminars')
        model = CourseEntity
        widgets = {
            'effects': FilteredSelectMultiple("efekty kształcenia", is_stacked=False)
        }


class ProposalDescriptionForm(ModelForm):
    class Meta:
        fields = ('description', 'requirements')
        model = CourseDescription
        widgets = {
            'description': forms.Textarea(attrs={'class': 'tinymce'}),
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }


class SyllabusForm(ModelForm):
    class Meta:
        fields = (
            'requirements',
            'studies_type',
            'year',
            'requirements',
            'objectives',
            'effects_txt',
            'contents',
            'learning_methods',
            'literature',
            'passing_form',
            'exam_hours',
            'tests_hours',
            'project_presentation_hours')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ProposalFormHelper()

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
            'status',
        ]
        help_texts = {
            'name': "Nazwa powinna być w języku wykładowym.",
            'name_en': "Dla przedmiotów po angielsku powinna być taka sama jak nazwa.",
            'short_name': "np. „JFiZO”, „AiSD” — nazwa do wyświetlania w planie zajęć.",
            'description': "Można formatować tekst używając Markdown.",
            'status': "Szkic można sobie zapisać na później."
        }


class CustomCheckbox(Field):
    """Renders Bootstrap 4 custom checkboxes.

    Inspired by
    https://simpleisbetterthancomplex.com/tutorial/2018/11/28/advanced-form-rendering-with-django-crispy-forms.html.
    """
    template = 'proposal/fields/custom_checkbox.html'


class Markdown(Field):
    """Renders textarea with Markdown preview.

    For the editor to work, the bundle 'proposal-markdown-editor' must be
    included in the template.
    """
    template = 'proposal/fields/markdown.html'


class FormRow(Div):
    """Represents Booststrap 4 form layout row."""
    css_class = 'form-row'


class ProposalFormHelper(FormHelper):
    """Defines layout for the Proposal form.

    Fields here must be the same as in `EditProposalForm`.
    """
    layout = Layout(
        Fieldset(
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
                    css_class='col-md-4 row px-4 align-items-center'),
            ),
            Markdown('description'),
            'status',
        ),
        Submit('submit', "Zapisz"),
    )

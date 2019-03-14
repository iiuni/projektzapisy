from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm
from django import forms
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription
from apps.offer.proposal.models import Syllabus, StudentWork


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

from django import forms
from django.forms.models import modelformset_factory

from apps.users.models import Employee

from .models import Preference


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ('answer', 'question', 'employee')
        labels = {
            'answer': "",
        }

    def __init__(self, *args, **kwargs):
        """Mark emplayee and question fields as hidden in the html.

        Now received values of these fields will be properly checked in is_valid.
        This will prevent null value insertion attempts if variables
        controlling the formset on the fornt-end are manipulated.
        """
        super().__init__(*args, **kwargs)
        self.fields['employee'].widget = forms.HiddenInput()
        self.fields['question'].widget = forms.HiddenInput()


def prepare_formset(employee: Employee, post=None):
    """Creates missing vote objects and returns a formset for the employee."""
    Preference.make_preferences(employee)
    PreferenceFormset = modelformset_factory(Preference, form=PreferenceForm, extra=0)
    qs = Preference.objects.filter(employee=employee).order_by('question__proposal')
    if post:
        formset = PreferenceFormset(post, queryset=qs)
    else:
        formset = PreferenceFormset(queryset=qs)
    return formset

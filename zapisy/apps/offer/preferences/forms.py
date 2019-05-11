from django import forms
from django.forms.models import modelformset_factory

from apps.users.models import Employee

from .models import Preference


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ('answer',)
        labels = {
            'answer': "",
        }


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

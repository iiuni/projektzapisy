from django import forms
from django.forms.models import modelformset_factory
from apps.offer.preferences.models import Preference


class PreferenceForm(forms.ModelForm):

    class Meta:
        model = Preference
        exclude = ('employee', 'proposal', )


PreferenceFormset = modelformset_factory(Preference, form=PreferenceForm, extra=0)

from django import forms
from django.forms.formsets import BaseFormSet, formset_factory

from apps.offer.desiderata.models import Desiderata, DesiderataOther

REVERSE_DAY = {
    '1': 'Poniedziałek',
    '2': 'Wtorek',
    '3': 'Środa',
    '4': 'Czwartek',
    '5': 'Piątek',
    '6': 'Sobota',
    '7': 'Niedziela'
}


class DesiderataOtherForm(forms.ModelForm):
    class Meta:
        model = DesiderataOther
        fields = ('comment', )
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 400, 'rows': 10}),
        }


class DesiderataForm(forms.Form):
    day = forms.CharField(widget=forms.HiddenInput)
    hour = forms.IntegerField(widget=forms.HiddenInput)
    value = forms.BooleanField(required=False)


class BaseDesiderataFormSet(BaseFormSet):
    def iter(self):
        result = {}
        for day in range(1, 8, 1):
            result[str(day)] = {}
            for hour in range(8, 22, 1):
                result[str(day)][hour] = 0
        for form in self.forms:
            if not form.is_bound:
                result[form.initial['day']][form.initial['hour']] = form
            else:
                result[form.data['day']][form.data['hour']] = form
        result = [(REVERSE_DAY[x[0]], x[1]) for x in sorted(result.items(), key=lambda x: x[0])]
        return iter(result)

    def hours(self):
        return range(8, 22)

    def save(self, desiderata, employee, semester):
        for form in self.forms:
            if form.is_valid():
                day = form.cleaned_data['day']
                hour = form.cleaned_data['hour']
                value = form.cleaned_data['value']
                if value is False and desiderata[day][hour] is None:
                    Desiderata.objects.create(
                        employee=employee, semester=semester, day=day, hour=hour)
                elif value and desiderata[day][hour] is not None:
                    Desiderata.objects.filter(
                        employee=employee, semester=semester, day=day, hour=hour).delete()


DesiderataFormSet = formset_factory(DesiderataForm, formset=BaseDesiderataFormSet, extra=0)

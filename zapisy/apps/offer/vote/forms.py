from django import forms

from apps.offer.proposal.models import Proposal, ProposalStatus
from apps.users.models import Student

from .models import SingleVote, SystemState


class SingleVoteForm(forms.ModelForm):
    class Meta:
        model = SingleVote
        fields = ('state', 'student', 'proposal', 'value',)
        widgets = {
            'state': forms.HiddenInput(),
            'student': forms.HiddenInput(),
            'proposal': forms.HiddenInput(),
            'entity': forms.HiddenInput(),
        }
        labels = {
            'value': "",
        }

    def save(self, commit=True):
        """We only will save votes that are not blank."""
        m = super().save(commit=False)
        if commit and m.value > 0:
            m.save()
        return m


class SingleCorrectionFrom(forms.ModelForm):
    class Meta:
        model = SingleVote
        fields = ['correction']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            value = self.instance.value
            self.fields['correction'].choices = filter(lambda v, l: v >= value,
                                                       SingleVote.VALUE_CHOICES)
            self.fields['correction'].default = value

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['correction'] < self.instance.value:
            raise forms.ValidationError(
                "Wartość w korekcie nie może być niższa niż w pierwszym głosowaniu.")
        return cleaned_data

    def save(self, commit=True):
        """We only will save votes that are not blank."""
        m = super().save(commit=False)
        if commit and m.correction > 0:
            m.save()
        return m


def prepare_vote_formset(state: SystemState, student: Student):
    SingleVote.create_missing_votes(student, state)
    formset_factory = forms.modelformset_factory(SingleVote, form=SingleVoteForm, extra=0)
    return formset_factory(queryset=SingleVote.objects.filter(state=state, student=student))

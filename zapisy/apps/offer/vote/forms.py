from django import forms

from apps.enrollment.courses.models import Semester
from apps.users.models import Student

from .models import SingleVote, SystemState


class SingleVoteForm(forms.ModelForm):
    class Meta:
        model = SingleVote
        fields = ('value',)
        labels = {'value': ""}

    def save(self, commit=True):
        super().save(commit=False)
        # This simple trick should radically save on number of queries.
        if commit and self.changed_data:
            self.instance.save()


class SingleCorrectionFrom(forms.ModelForm):
    class Meta:
        model = SingleVote
        fields = ('correction', )
        labels = {'correction': ""}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            value = self.instance.value
            self.fields['correction'].choices = filter(lambda v: v[0] >= value,
                                                       SingleVote.VALUE_CHOICES)
            self.fields['correction'].default = value

    def clean(self):
        cleaned_data = super().clean()
        if 'correction' not in cleaned_data:
            raise forms.ValidationError("Wartość korekty musi być podana.")
        if cleaned_data['correction'] < self.instance.value:
            raise forms.ValidationError(
                "Wartość w korekcie nie może być niższa niż w pierwszym głosowaniu.")
        return cleaned_data

    def save(self, commit=True):
        super().save(commit=False)
        # This simple trick should radically save on number of queries.
        if commit and self.changed_data:
            self.instance.save()


class SingleVoteFormset(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.limit = kwargs.pop('limit', None)
        if self.limit is None:
            self.limit = SystemState.DEFAULT_MAX_POINTS
        super().__init__(*args, **kwargs)

    def clean(self):
        """Checks that the points limit is not exceeded."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on
            # its own
            return
        total = 0
        for form in self.forms:
            # Some proposal types are free to vote for.
            if form.instance.proposal.course_type.free_in_vote:
                continue
            form_value = form.cleaned_data.get('value', 0)
            form_correction = form.cleaned_data.get('correction', 0)
            total += form_correction or form_value
        if total > self.limit:
            raise forms.ValidationError(
                f"Suma przyznanych punktów nie może przekraczać {self.limit}.")


def prepare_vote_formset(state: SystemState, student: Student, post=None):
    """Constructs a formset for voting or correction.

    It is assumed that the voting/correction is currently active. The function
    will fail otherwise.
    """
    SingleVote.create_missing_votes(student, state)

    queryset = SingleVote.objects.filter(
        state=state, student=student).select_related('proposal', 'proposal__course_type').only(
            'value', 'correction', 'proposal__name', 'proposal__slug',
            'proposal__course_type', 'proposal__course_type__free_in_vote', 'proposal__semester')
    if state.is_vote_active():
        FormClass = SingleVoteForm
        limit = SystemState.DEFAULT_MAX_POINTS
        queryset = queryset.in_vote()
    elif state.correction_active_semester() is not None:
        semester: Semester = state.correction_active_semester()
        limit = SingleVote.points_for_semester(student, state, semester.type)
        FormClass = SingleCorrectionFrom
        queryset = queryset.in_semester(semester=semester)
    else:
        raise AssertionError("Voting or Correction must be active.")

    formset_factory = forms.modelformset_factory(
        SingleVote, formset=SingleVoteFormset, form=FormClass, extra=0)
    if post:
        formset = formset_factory(post, limit=limit)
    else:
        formset = formset_factory(queryset=queryset, limit=limit)
    return formset

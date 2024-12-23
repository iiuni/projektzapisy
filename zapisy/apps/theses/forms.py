from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.utils import timezone

from apps.common import widgets as common_widgets
from apps.theses.enums import ThesisKind, ThesisStatus, ThesisVote
from apps.theses.models import MAX_THESIS_TITLE_LEN, Remark, Thesis, Vote
from apps.users.models import Employee, Student
from apps.theses.validators import MAX_MAX_ASSIGNED_STUDENTS


class ThesisFormAdmin(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = '__all__'


class RemarkFormAdmin(forms.ModelForm):
    class Meta:
        model = Remark
        fields = '__all__'


class VoteFormAdmin(forms.ModelForm):
    class Meta:
        model = Vote
        fields = '__all__'


class ThesisFormBase(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = '__all__'

    title = forms.CharField(label="Tytuł pracy", max_length=MAX_THESIS_TITLE_LEN)
    advisor = forms.ModelChoiceField(queryset=Employee.objects.none(),
                                     label="Promotor",
                                     required=True,
                                     empty_label=None)
    supporting_advisor = forms.ModelChoiceField(queryset=Employee.objects.none(),
                                                label="Promotor wspierający",
                                                required=False)
    kind = forms.TypedChoiceField(choices=ThesisKind.choices, label="Typ", coerce=int)
    all_students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        required=False,
        label="Studenci",
        widget=forms.SelectMultiple(attrs={'size': '10'}))
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        required=False,
        label="Wybrani studenci",
        widget=forms.SelectMultiple(attrs={'size': '10'}))
    reserved_until = forms.DateField(help_text="Jeżeli przypiszesz do pracy studentów, "
                                     "uzupełnij również datę rezerwacji.",
                                     widget=forms.TextInput(attrs={'type': 'date'}),
                                     label="Zarezerwowana do",
                                     required=False)
    description = forms.CharField(
        label="Opis", widget=common_widgets.MarkdownArea, required=False)
    max_number_of_students = forms.TypedChoiceField(
        label="Maks. liczba studentów", coerce=int,
        choices=tuple((i, i) for i in range(1, MAX_MAX_ASSIGNED_STUDENTS + 1))
    )
    user_input = forms.CharField(
        label="Znajdź studenta",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filtruj po imieniu, nazwisku, numerze indeksu'})
    )
    selected_students = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, user, *args, **kwargs):
        super(ThesisFormBase, self).__init__(*args, **kwargs)

        self.fields['advisor'].queryset = Employee.objects.filter(
            pk=user.employee.pk)
        self.fields['advisor'].initial = user.employee

        self.can_assign_multiple_students = user.has_perm('theses.assign_multiple_students')

        self.fields['supporting_advisor'].queryset = Employee.objects.exclude(
            pk=user.employee.pk)

        self.fields['status'].required = False

        if 'selected_students' in self.data:
            selected_student_ids = [int(sid) for sid in self.data.get('selected_students').split(',') if sid.isdigit()]
            self.update_students_queryset(Student.objects.filter(id__in=selected_student_ids))
            self.data = self.data.copy()
            self.data.setlist('students', selected_student_ids)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            'title',
            Row(Column('advisor', css_class='form-group col-md-6 mb-0'),
                Column('supporting_advisor', css_class='form-group col-md-6 mb-0'),
                css_class='row'),
            Row(
                Column('kind', css_class='form-group col-md-3'),
                Column('max_number_of_students', css_class='form-group col-md-3'),
                Column('reserved_until', css_class='form-group col-md-6'),
                css_class='row'),
            'user_input',
            Row(
                Column('all_students', css_class='form-group col-md-6'),
                Column('students', css_class='form-group col-md-6'),
                css_class='row'),
            'description',
        )
        self.helper.add_input(
            Submit('submit', 'Zapisz', css_class='btn-primary'))

    def update_students_queryset(self, queryset):
        self.fields['students'].queryset = queryset

    def clean_students(self):
        selected_student_ids = self.cleaned_data.get('selected_students', '')
        if selected_student_ids:
            student_ids = [int(sid) for sid in selected_student_ids.split(',') if sid.isdigit()]
            students = Student.objects.filter(id__in=student_ids)
            return students
        return []

    def clean(self):
        self.cleaned_data['students'] = self.clean_students()
        super().clean()
        students = self.cleaned_data['students']
        max_number_of_students = int(self.cleaned_data['max_number_of_students'])
        if ('students' in self.changed_data or 'max_number_of_students' in self.changed_data) \
                and len(students) > max_number_of_students:
            raise forms.ValidationError('Przekroczono limit przypisanych studentów.')
        if 'students' in self.data and self.cleaned_data['reserved_until'] is None:
            raise forms.ValidationError("Do pracy przypisano studenta. Uzupełnij datę rezerwacji")
        if 'students' not in self.data and self.cleaned_data['reserved_until'] is not None:
            raise forms.ValidationError("Nie przypisano studentów do pracy. Usuń datę rezerwacji")


class ThesisForm(ThesisFormBase):
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.added = timezone.now()
        instance.status = ThesisStatus.BEING_EVALUATED.value

        instance.save()
        self.save_m2m()

        return instance


class EditThesisForm(ThesisFormBase):
    def __init__(self, user, *args, **kwargs):
        super(EditThesisForm, self).__init__(user, *args, **kwargs)

        self.status = self.instance.status

        if self.instance and self.instance.pk:
            student_ids = self.instance.students.values_list('pk', flat=True)
            self.fields['students'].queryset = Student.objects.filter(pk__in=student_ids)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.modified = timezone.now()

        status = self.status

        if len(set(self.changed_data).intersection([
                'title', 'supporting_advisor', 'kind',
                'max_number_of_students', 'description'])) > 0:
            instance.status = ThesisStatus.BEING_EVALUATED.value
        elif status == ThesisStatus.ACCEPTED.value and 'students' in self.data:
            instance.status = ThesisStatus.IN_PROGRESS.value
        elif status == ThesisStatus.IN_PROGRESS.value and 'students' not in self.data:
            instance.status = ThesisStatus.ACCEPTED.value
        else:
            instance.status = status

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class RemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['text']

    text = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': '5'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.thesis = kwargs.pop('thesis', None)
        if self.thesis is not None:
            try:
                instance = self.thesis.thesis_remarks.all().get(author=self.user.employee)
            except Remark.DoesNotExist:
                instance = None

            kwargs['instance'] = instance

        super(RemarkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_method = 'POST'
        self.helper.add_input(
            Submit('submit', 'Zapisz', css_class='btn-primary'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if getattr(instance, 'author', None) is None:
            instance.author = self.user.employee
        if getattr(instance, 'thesis', None) is None:
            instance.thesis = self.thesis
        if commit:
            instance.modified = timezone.now()
            instance.save()

        return instance


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['vote']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        _vote = kwargs.pop('vote', None)
        self.thesis = kwargs.pop('thesis', None)

        if self.thesis is not None:
            try:
                instance = self.thesis.thesis_votes.get(
                    owner=self.user.employee)
            except Vote.DoesNotExist:
                instance = None

            kwargs['instance'] = instance

        super(VoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.fields['vote'].widget = forms.HiddenInput()

        if _vote is not None:
            self.fields['vote'].initial = _vote.value

        if _vote == ThesisVote.ACCEPTED:
            self.helper.add_input(
                Submit('submit', 'Zaakceptuj', css_class='btn btn-success'))
        elif _vote == ThesisVote.REJECTED:
            self.helper.add_input(
                Submit('submit', 'Odrzuć', css_class='btn btn-danger'))
        else:
            self.helper.add_input(
                Submit('submit', 'Cofnij głos', css_class='btn btn-primary'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if getattr(instance, 'owner', None) is None:
            instance.owner = self.user.employee
        if getattr(instance, 'thesis', None) is None:
            instance.thesis = self.thesis
        if commit:
            instance.save()
        return instance


class RejecterForm(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = ['status']

    def __init__(self, *args, **kwargs):
        status = kwargs.pop('status', None)
        super(RejecterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.fields['status'].widget = forms.HiddenInput()

        if status is not None:
            self.fields['status'].initial = status.value

        if status == ThesisStatus.ACCEPTED:
            self.helper.add_input(
                Submit('submit', 'Zaakceptuj', css_class='btn btn-sm btn-success'))
        elif status == ThesisStatus.RETURNED_FOR_CORRECTIONS:
            self.helper.add_input(
                Submit('submit', 'Zwróć do poprawek', css_class='btn btn-sm btn-danger'))
        else:
            self.helper.add_input(
                Submit('submit', 'Zwróć do głosowania', css_class='btn btn-sm'))

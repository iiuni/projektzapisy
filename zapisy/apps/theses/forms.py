from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, HTML, Field, Div
from apps.theses.models import Thesis, Remark, Vote, MAX_THESIS_TITLE_LEN, MAX_ASSIGNED_STUDENTS
from apps.theses.enums import ThesisKind, ThesisStatus, ThesisVote
from apps.theses.system_settings import change_status
from apps.users.models import Employee, Student


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

    title = forms.CharField(label="Tytuł pracy",
                            max_length=MAX_THESIS_TITLE_LEN)
    advisor = forms.ModelChoiceField(
        queryset=Employee.objects.none(), label="Promotor", required=True)
    supporting_advisor = forms.ModelChoiceField(queryset=Employee.objects.none(),
                                                label="Promotor wspierający", required=False)
    kind = forms.ChoiceField(choices=ThesisKind.choices, label="Typ")
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.all(), required=False, label="Przypisani studenci",
                                              widget=forms.SelectMultiple(attrs={'size': '10'}))
    status = forms.ChoiceField(choices=ThesisStatus.choices, label="Status")
    reserved_until = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}),
                                     label="Zarezerwowana do", required=False)
    description = forms.CharField(
        label="Opis", widget=forms.Textarea, required=False)

    def __init__(self, user, *args, **kwargs):
        super(ThesisFormBase, self).__init__(*args, **kwargs)
        self.is_staff = False
        if user.is_staff:
            self.is_staff = True
            self.fields['advisor'].queryset = Employee.objects.all()
        else:
            self.fields['advisor'].queryset = Employee.objects.filter(
                pk=user.employee.pk)
            self.fields['advisor'].initial = user.employee
            self.fields['advisor'].widget.attrs['readonly'] = True
        self.fields['supporting_advisor'].queryset = Employee.objects.exclude(
            pk=user.employee.pk)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

    def clean_students(self):
        students = self.cleaned_data['students']
        if len(students) > MAX_ASSIGNED_STUDENTS:
            raise forms.ValidationError(
                "Możesz przypisać maksymalnie " + str(MAX_ASSIGNED_STUDENTS) + " studentów")
        return students


class ThesisForm(ThesisFormBase):
    def __init__(self, user, *args, **kwargs):
        super(ThesisForm, self).__init__(user, *args, **kwargs)

        if user.is_staff:
            self.fields['status'].required = True
            row_1 = Row(
                Column('kind', css_class='form-group col-md-2'),
                Column('reserved_until', css_class='form-group col-md-4'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'
            )
        else:
            self.fields['status'].required = False
            row_1 = Row(
                Column('kind', css_class='form-group col-md-6'),
                Column('reserved_until', css_class='form-group col-md-6'),
                css_class='form-row'
            )

        self.helper.layout = Layout(
            'title',
            Row(
                Column('advisor', css_class='form-group col-md-6 mb-0'),
                Column('supporting_advisor',
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            row_1,
            Div('students',
                HTML('<small class="form-text text-muted ">Przytrzymaj wciśnięty klawisz „Ctrl” lub „Command” na Macu, aby zaznaczyć więcej niż jeden wybór.</small>'), css_class='mb-3'),
            'description',
        )

        self.helper.add_input(
            Submit('submit', 'Zapisz', css_class='btn-primary'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.added = timezone.now()

        if not self.is_staff:
            instance.status = ThesisStatus.BEING_EVALUATED.value

        instance.save()
        self.save_m2m()

        return instance


class EditThesisForm(ThesisFormBase):
    def __init__(self, user, *args, **kwargs):
        super(EditThesisForm, self).__init__(user, *args, **kwargs)

        self.status = self.instance.status

        if user.is_staff:
            special_row = Row(
                Column('kind', css_class='form-group col-md-2'),
                Column('reserved_until', css_class='form-group col-md-4'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'
            )
        else:
            self.fields['status'].required = False
            special_row = Row(
                Column('kind', css_class='form-group col-md-6'),
                Column('reserved_until', css_class='form-group col-md-6'),
                css_class='form-row'
            )

        self.helper.layout = Layout(
            'title',
            Row(
                Column('advisor', css_class='form-group col-md-6 mb-0'),
                Column('supporting_advisor',
                       css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            special_row,
            Div('students',
                HTML('<small class="form-text text-muted ">Przytrzymaj wciśnięty klawisz „Ctrl” lub „Command” na Macu, aby zaznaczyć więcej niż jeden wybór.</small>'), css_class='mb-3'),
            'description',
        )
        if self.instance.is_returned and self.instance.is_mine(user):
            self.helper.add_input(
                Submit('submit', 'Zapisz i prześlij do komisji', css_class='btn-primary'))
        else:
            self.helper.add_input(
                Submit('submit', 'Zapisz', css_class='btn-primary'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.modified = timezone.now()

        if not self.is_staff:
            status = self.status

            if status == ThesisStatus.RETURNED_FOR_CORRECTIONS.value:
                instance.status = ThesisStatus.BEING_EVALUATED.value
            elif status == ThesisStatus.ACCEPTED.value and "students" in self.data:
                instance.status = ThesisStatus.IN_PROGRESS.value
            elif status == ThesisStatus.IN_PROGRESS.value and "students" not in self.data:
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
        thesis = instance.thesis

        # check number of votes and change thesis status
        change_status(thesis, instance.vote)

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

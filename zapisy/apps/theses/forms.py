from django import forms
from .models import Thesis
from .defs import MAX_STUDENTS_PER_THESIS


class ThesisForm(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = '__all__'

    def clean(self):
        """
        Custom validation: ensure that the students limit hasn't been exceeded.
        """
        students = self.cleaned_data.get('students')
        if students and len(students) > MAX_STUDENTS_PER_THESIS:
            raise forms.ValidationError(
                f'Do pracy dyplomowej można przypisać co najwyżej {MAX_STUDENTS_PER_THESIS} studentów.'
            )
        return self.cleaned_data

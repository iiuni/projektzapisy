from django import forms
from django.contrib.auth.models import User

from .models import Employee


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Adres jest już użyty przez innego użytkownika")


class EmployeeDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('title', 'room', 'homepage', 'consultations',)

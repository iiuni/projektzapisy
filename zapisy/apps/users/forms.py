from django import forms
from django.contrib.auth.models import User
from django.db import models

from .models import Employee


class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Adres jest już użyty przez innego użytkownika")
        return email


def formfield_assuming_https(db_field, **kwargs):
    """Makes URL fields prepend 'https://' to addresses entered without a scheme."""
    if isinstance(db_field, models.URLField):
        kwargs['assume_scheme'] = 'https'
    return db_field.formfield(**kwargs)


class EmployeeDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('title', 'room', 'homepage', 'consultations',)
        formfield_callback = formfield_assuming_https

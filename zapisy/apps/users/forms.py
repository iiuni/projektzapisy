from django import forms
from django.contrib.auth.models import User

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


class EmployeeDataForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('title', 'room', 'homepage', 'consultations',)

    def __init__(self, *args, **kwargs):
        super(EmployeeDataForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'my-2'
        self.fields['room'].widget.attrs['class'] = 'my-2'
        self.fields['homepage'].widget.attrs['class'] = 'my-2'
        self.fields['consultations'].widget.attrs['class'] = 'my-2'

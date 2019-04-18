from django import forms
from django.contrib.auth.models import User

from apps.users.models import Employee


class EmailChangeForm(forms.ModelForm):
    class Meta:
        fields = ['email']
        model = User


class ConsultationsChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConsultationsChangeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"
            visible.field.widget.attrs['size'] = 41

    class Meta:
        fields = ['title', 'room', 'homepage', 'consultations']
        model = Employee


class EmailToAllStudentsForm(forms.Form):
    sender = forms.EmailField(label="Nadawca")
    subject = forms.CharField(label="Temat", max_length=100)
    message = forms.CharField(label="Wiadomość", widget=forms.widgets.Textarea(
        attrs={'cols': 80,
               'rows': 8}))
    cc_myself = forms.BooleanField(label="Wyślij kopię do mnie", required=False)

from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher
from django.forms import ModelForm


class PreferencesFormStudent(ModelForm):
    class Meta:
        model = NotificationPreferencesStudent
        exclude = ['user']


class PreferencesFormTeacher(ModelForm):
    class Meta:
        model = NotificationPreferencesTeacher
        exclude = ['user']

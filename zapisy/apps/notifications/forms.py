from django.forms import ModelForm

from apps.notifications.models import NotificationPreferencesStudent, NotificationPreferencesTeacher


class PreferencesFormStudent(ModelForm):
    class Meta:
        model = NotificationPreferencesStudent
        exclude = ['user']


class PreferencesFormTeacher(ModelForm):
    class Meta:
        model = NotificationPreferencesTeacher
        exclude = ['user']

from django import forms
from django.forms.models import modelformset_factory
from apps.notifications.models import NotificationPreferences, get_category

__author__ = 'maciek'


class NotificationForm(forms.ModelForm):

    def category(self):
        return get_category(self.instance.type)

    class Meta:
        fields = ('value',)
        model = NotificationPreferences


NotificationFormset = modelformset_factory(
    NotificationPreferences,
    form=NotificationForm,
    extra=0,
    can_delete=False)

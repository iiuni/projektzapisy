from django import forms
from django.contrib import admin

from .models.specialreservation import SpecialReservation
from .models.term import Term


class SpecialReservationForm(forms.ModelForm):

    ignore_conflicts = forms.BooleanField(required=False, label="", widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(SpecialReservationForm, self).__init__(*args, **kwargs)
        if self.errors:
            if '__all__' in self.errors:
                if 'W tym samym czasie' in self.errors['__all__'].as_ul():
                    self.fields['ignore_conflicts'].widget = forms.CheckboxInput()
                    self.fields['ignore_conflicts'].label = 'Zezwalaj na konflikty'
                    self._errors['ignore_conflicts'] = self.error_class(['Zaakceptuj konflikty'])

    def clean(self):
        cleaned_data = super(SpecialReservationForm, self).clean()
        self.instance.ignore_conflicts = cleaned_data.get('ignore_conflicts')
        return cleaned_data

    class Meta:
        model = SpecialReservation
        fields = '__all__'


class SpecialReservationAdmin(admin.ModelAdmin):
    form = SpecialReservationForm

    list_display = ('title', 'classroom', 'dayOfWeek', 'start_time', 'end_time', 'semester')
    list_filter = ('semester', )
    search_fields = ('title', )
    ordering = ('semester', 'dayOfWeek')

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.save(author_id=request.user.id)
        return instance


class TermAdmin(admin.ModelAdmin):
    list_display = ('event', 'day', 'start', 'end', 'room', 'place')
    list_filter = ('room',)
    search_fields = ('event__title',)
    ordering = ('-day', 'start', 'end')


admin.site.register(Term, TermAdmin)
admin.site.register(SpecialReservation, SpecialReservationAdmin)

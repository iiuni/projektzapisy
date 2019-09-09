from django.contrib import admin
from django import forms

from apps.grade.poll.models.template import Template
from apps.grade.poll.models.saved_ticket import SavedTicket


class PollAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PollAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = self.fields['group'].queryset.select_related(
            'course', 'course', 'teacher', 'teacher__user')
        self.fields['author'].queryset = self.fields['author'].queryset.select_related('user')


class PollAdmin(admin.ModelAdmin):
    list_filter = ('semester',)
    search_fields = ('title',)
    form = PollAdminForm


class TemplateAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(TemplateAdmin, self).get_queryset(request)
        return qs.select_related('studies_type', 'author', 'author__user')


admin.site.register(SavedTicket)
admin.site.register(Template, TemplateAdmin)

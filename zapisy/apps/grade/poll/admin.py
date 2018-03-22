"""
    Django admin panel for polls
"""

from django.contrib import admin
from django import forms

from apps.grade.poll.models.option import Option
from apps.grade.poll.models.open_question import OpenQuestion, OpenQuestionOrdering
from apps.grade.poll.models.multiple_choice_question import MultipleChoiceQuestion, MultipleChoiceQuestionOrdering
from apps.grade.poll.models.single_choice_question import SingleChoiceQuestion, SingleChoiceQuestionOrdering
from apps.grade.poll.models.section import Section, SectionOrdering
from apps.grade.poll.models.template import Template, TemplateSections
from apps.grade.poll.models.open_question_answer import OpenQuestionAnswer
from apps.grade.poll.models.single_choice_question_answer import SingleChoiceQuestionAnswer
from apps.grade.poll.models.multiple_choice_question_answer import MultipleChoiceQuestionAnswer
from apps.grade.poll.models.saved_ticket import SavedTicket

from apps.grade.poll.models.poll import Poll


class PollAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PollAdminForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = self.fields['group'].queryset.select_related(
            'course', 'course__entity', 'teacher', 'teacher__user')
        self.fields['author'].queryset = self.fields['author'].queryset.select_related('user')


class PollAdmin(admin.ModelAdmin):
    list_filter = ('semester', )
    search_fields = ('title', )
    form = PollAdminForm

#    def queryset(self, request):
#       qs = super(PollAdmin, self).queryset(request)
# return qs.select_related('author', 'author__user', 'group',
# 'group__course', 'group__teacher', 'group__teacher__user')


class TemplateAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(TemplateAdmin, self).get_queryset(request)
        return qs.select_related('studies_type', 'course', 'author', 'author__user')


#admin.site.register( Option )
#admin.site.register( OpenQuestionOrdering )
#admin.site.register( SingleChoiceQuestionOrdering )
#admin.site.register( MultipleChoiceQuestionOrdering )
#admin.site.register( SectionOrdering )
#admin.site.register( OpenQuestion )
#admin.site.register( SingleChoiceQuestion )
#admin.site.register( MultipleChoiceQuestion )
#admin.site.register( Section )
#admin.site.register( Poll, PollAdmin )
admin.site.register(SavedTicket)
#admin.site.register( OpenQuestionAnswer )
#admin.site.register( SingleChoiceQuestionAnswer )
#admin.site.register( MultipleChoiceQuestionAnswer )
admin.site.register(Template, TemplateAdmin)

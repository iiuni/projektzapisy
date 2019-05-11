from django.contrib import admin

from .models import PreferencesQuestion, Preference


@admin.register(PreferencesQuestion)
class PreferencesQuestionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['proposal']


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'proposal', 'class_type', 'answer')
    list_filter = (('employee', admin.RelatedOnlyFieldListFilter),
                   ('question__proposal',
                    admin.RelatedOnlyFieldListFilter), 'question__class_type', 'answer')

    def proposal(self, obj):
        return obj.question.proposal

    def class_type(self, obj):
        return obj.question.get_class_type_display()

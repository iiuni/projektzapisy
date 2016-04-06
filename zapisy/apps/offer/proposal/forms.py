# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelForm
from apps.enrollment.courses.models.course import CourseEntity, CourseDescription


class ProposalForm(ModelForm):
    class Meta:
        fields = ('name', 'type', 'exam', 'english', 'semester', 'web_page','effects')
        model = CourseEntity
        widgets = {
            'effects': FilteredSelectMultiple(u"efekty kształcenia", is_stacked=False)
        }

class ProposalDescriptionForm(ModelForm):
    class Meta:
        fields = ('description', 'requirements')
        model = CourseDescription
        widgets = {
            'requirements': FilteredSelectMultiple("wymagania", is_stacked=False)
        }


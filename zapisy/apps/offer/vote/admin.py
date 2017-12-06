# -*- coding: utf-8 -*-

"""
    Django admin panel for vote
"""

from datetime import date

from django.contrib import admin
from django.forms   import ModelForm
from django.forms   import ValidationError

from apps.offer.vote.models import SystemState, SingleVote

class SystemStateAdminForm( ModelForm ):
    """
        Admin form for system state
    """
    class Meta:
        model = SystemState
        fields = '__all__'

    def clean_max_points(self):
        """
            Max points per courses validation
        """
        data = self.cleaned_data['max_points']

        if data < 1:
            raise ValidationError("Musi wynosić co najmniej 1.")

        return data


class SingleVoteAdmin( admin.ModelAdmin ):
    raw_id_fields = ('student', 'entity', 'course')
    list_display = ('student', 'entity','value', 'correction', 'state')
    list_filter = ('correction', 'state', 'entity', 'course__semester')
    search_fields = ('student__matricula', 'student__user__first_name', 'student__user__last_name', 'student__user__username', 'entity__name')

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super(SingleVoteAdmin, self).get_queryset(request)
        return qs.select_related('student', 'student__user', 'course', 'course__semester', 'course__type', 'entity',
            'proposal', 'state')

class StateAdmin( admin.ModelAdmin ):
    """
        System State Administration
    """
    form = SystemStateAdminForm

admin.site.register( SystemState, StateAdmin )
admin.site.register( SingleVote, SingleVoteAdmin )

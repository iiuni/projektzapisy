"""
    Preferences admin
"""

from django.contrib import admin
from django.db.models import Q

from apps.offer.preferences.models import Preference


class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'proposal',
        'lecture',
        'review_lecture',
        'tutorial',
        'lab',
        'tutorial_lab',
        'seminar',
    )
    list_filter = ('employee', 'proposal',)
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'proposal__name')

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super(PreferenceAdmin, self).get_queryset(request)
        return qs.filter(
            Q(
                lecture__isnull=False) | Q(
                review_lecture__isnull=False) | Q(
                tutorial__isnull=False) | Q(
                    lab__isnull=False) | Q(
                        tutorial_lab__isnull=False) | Q(
                            seminar__isnull=False))

admin.site.register(Preference, PreferenceAdmin)

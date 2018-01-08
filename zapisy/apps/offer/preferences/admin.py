# -*- coding: utf-8 -*-

"""
    Preferences admin
"""

from django.contrib import admin
from django.db.models import Q

from apps.offer.preferences.models import Preference

class PreferenceAdmin(admin.ModelAdmin):
    list_display =  ('employee', 'proposal', 'lecture', 'review_lecture','tutorial','lab','tutorial_lab','seminar',)
    list_filter = ('employee', 'proposal',)
    search_fields = ('employee__user__first_name','employee__user__last_name', 'proposal__name')

    def get_queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(PreferenceAdmin, self).get_queryset(request)
       return qs.filter(Q(lecture__isnull=False)|Q(review_lecture__isnull=False)
                        |Q(tutorial__isnull=False)|Q(lab__isnull=False)|Q(tutorial_lab__isnull=False)
                        |Q(seminar__isnull=False))


#    list_display = ('course', 'teacher','type','limit','limit_zamawiane','get_terms_as_string')
#    list_filter = ('type', 'course__semester', 'teacher')
#    search_fields = ('teacher__user__first_name','teacher__user__last_name','course__name')
#    inlines = [
#        TermInline,RecordInline
#    ]
#
#    raw_id_fields = ('course', 'teacher')
#
#    def changelist_view(self, request, extra_context=None):
#
#        if not request.GET.has_key('course__semester__id__exact'):
#
#            q = request.GET.copy()
#            semester = Semester.get_current_semester()
#            q['course__semester__id__exact'] = semester.id
#            request.GET = q
#            request.META['QUERY_STRING'] = request.GET.urlencode()
#        return super(GroupAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(Preference, PreferenceAdmin)

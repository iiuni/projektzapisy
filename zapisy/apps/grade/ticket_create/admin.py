# -*- coding: utf-8 -*-
from django.contrib                    import admin
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp, StudentGraded


class StudentGradedAdmin( admin.ModelAdmin ):
    list_display = ('student',  'semester')
    search_fields = ('student__user__first_name',
                     'student__user__last_name',
                     'student__matricula',)

    list_filter = ('semester',)

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super(StudentGradedAdmin, self).get_queryset(request)
        return qs.select_related('semester', 'student', 'student__user')


class UsedTicketStampAdmin( admin.ModelAdmin ):
    list_display = ['student', 'poll' ]
    search_fields = ('student__user__first_name',
                     'student__user__last_name',
                     'student__matricula',)

class PrivateKeyAdmin( admin.ModelAdmin ):

    list_display = ('poll', )
    search_fields = ('poll__title',)

admin.site.register( PublicKey )
admin.site.register( PrivateKey, PrivateKeyAdmin )
admin.site.register( UsedTicketStamp, UsedTicketStampAdmin )
admin.site.register( StudentGraded, StudentGradedAdmin )


from django.contrib import admin
from apps.enrollment.records.models import *

#
# class RecordAdmin(admin.ModelAdmin):
#     list_display = ('__str__','student','status','get_semester_name')
#     search_fields = ('student__matricula','student__user__first_name','student__user__last_name','group__course__name','group__course__semester__year','group__course__semester__type')
#     list_filter = ('status',)
#
# class QueueAdmin(admin.ModelAdmin):
#     list_display = ('group', 'time', 'student')
#     search_fields = ('student__matricula','student__user__first_name','student__user__last_name','group__course__name')
#     list_filter = ('group__course__semester', 'group__type')
#
#     raw_id_fields = ('group', 'student')
#
#     def queryset(self, request):
#        """
#        Filter the objects displayed in the change_list to only
#        display those for the currently signed in user.
#        """
#        qs = super(QueueAdmin, self).queryset(request)
#        return qs.select_related('student', 'student__user', 'group', 'group__course',  'group__course__entity','group__course__semester', 'group__teacher', 'group__teacher__user')
#
# admin.site.register( Record, RecordAdmin )
# admin.site.register( Queue, QueueAdmin )

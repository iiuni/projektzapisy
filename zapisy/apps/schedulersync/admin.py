from django.contrib import admin

from .models import CourseMap, EmployeeMap


class CourseMapAdmin(admin.ModelAdmin):
    list_display = ('scheduler_course', 'proposal')
    search_fields = ('scheduler_course', 'proposal__name', 'proposal__name_en')
    ordering = ('scheduler_course',)


class EmployeeMapAdmin(admin.ModelAdmin):
    list_display = ('scheduler_username', 'employee')
    search_fields = ('scheduler_username', 'employee__user__first_name', 'employee__user__last_name')
    ordering = ('scheduler_username',)


admin.site.register(EmployeeMap, EmployeeMapAdmin)
admin.site.register(CourseMap, CourseMapAdmin)

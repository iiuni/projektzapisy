from django.contrib import admin
from apps.enrollment.courses.models.semester import Semester
from .models import EmployeeMap, CourseMap


class CourseMapAdmin(admin.ModelAdmin):
    list_filter = ('course__semester',)
    list_display = ('scheduler_course', 'course')
    search_fields = ('scheduler_course', 'course__offer__name', 'course__offer__name_en')
    ordering = ('course__semester', 'scheduler_course')


class EmployeeMapAdmin(admin.ModelAdmin):
    list_display = ('scheduler_username', 'employee')
    search_fields = ('scheduler_username', 'employee__user__first_name', 'employee__user__last_name')
    ordering = ('scheduler_username',)


admin.site.register(EmployeeMap, EmployeeMapAdmin)
admin.site.register(CourseMap, CourseMapAdmin)

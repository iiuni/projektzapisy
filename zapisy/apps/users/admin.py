from django.http import HttpResponse, HttpRequest
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import QuerySet
import csv

from apps.users.models import (
    Employee,
    Student,
    Program)
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record


class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Dane osobowe', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dodatkowe dane', {'fields': ('is_student', 'is_employee')}),
        ('Uprawnienia', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined')}),
        ('Grupy', {'fields': ('groups',)})
    ]
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_employee')
    search_fields = ('username', 'first_name', 'last_name', 'email')


def export_as_csv(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
    semester = Semester.get_current_semester()

    records = Record.objects.filter(
        student__in=queryset,
        group__course__semester=semester,
        status=1).select_related(
        'student',
        'student__user',
        'group',
        'group__course')

    opts = modeladmin.model._meta

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

    writer = csv.writer(response)
    for record in records:
        writer.writerow([record.student.matricula,
                         record.student.user.first_name,
                         record.student.user.last_name,
                         record.group.course.name,
                         record.group.get_type_display(),
                         record.group.get_terms_as_string()])
    return response


export_as_csv.short_description = "Export jako CSV"


class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'get_full_name', 'ects', 'get_type_of_studies')
    fieldsets = [
        (None, {'fields': ['user', 'matricula', 'status']}),
        ('Studia', {'fields': ['numeryczna_l', 'dyskretna_l', 'program', 'semestr', 'ects']}),
        ('Zapisy', {'fields': ['records_opening_bonus_minutes', 'block']}),
        ('Inne', {'fields': ['receive_mass_mail_enrollment', 'receive_mass_mail_offer', 'receive_mass_mail_grade', 'last_news_view'], 'classes': ['collapse']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program', 'status', 'semestr')
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)
    list_max_show_all = 9999

    actions = [export_as_csv]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.select_related('program', 'user')


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'homepage', 'room', 'consultations',)
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None, {
            'fields': [
                'user', 'status', 'homepage', 'room', 'consultations']}), ('Ogłoszenia mailowe', {
                    'fields': [
                        'receive_mass_mail_enrollment', 'receive_mass_mail_offer'], 'classes': ['collapse']}), ]
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super(EmployeeAdmin, self).get_queryset(request)
        return qs.select_related('user')


class StudentInline(admin.StackedInline):
    model = Student
    extra = 0
    max_num = 1


class EmployeeInline(admin.StackedInline):
    model = Employee
    extra = 0
    max_num = 1


class UserAdmin(DjangoUserAdmin):
    inlines = [StudentInline, EmployeeInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program)

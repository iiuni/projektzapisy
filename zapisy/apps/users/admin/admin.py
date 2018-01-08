# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

import unicodecsv

from apps.users.models import (Employee, Student, Program, StudiaZamawiane, StudiaZamawianeMaileOpiekunow, UserProfile,
                               StudiaZamawiane2012)
from apps.enrollment.courses.models import Semester
from apps.enrollment.records.models import Record


class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Dane osobowe', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dodatkowe dane', {'fields': ('is_student', 'is_employee', 'is_zamawiany')}),
        ('Uprawnienia', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined')}),
        ('Grupy', {'fields': ('groups',)})
    ]
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_employee', 'is_zamawiany')
    search_fields = ('username', 'first_name', 'last_name', 'email')


def export_as_csv(modeladmin, request, queryset):
    semester = Semester.get_current_semester()

    records = Record.objects.filter(student__in=queryset, group__course__semester=semester, status=1).select_related(
        'student', 'student__user', 'group', 'group__course')

    opts = modeladmin.model._meta

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

    writer = unicodecsv.writer(response, encoding='utf-8')
    for record in records:
        writer.writerow([record.student.matricula, record.student.user.first_name, record.student.user.last_name,
                         record.group.course.name, record.group.get_type_display(), record.group.get_terms_as_string()])
    return response


export_as_csv.short_description = "Export jako CSV"



class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula','get_full_name','ects','get_type_of_studies')
    fieldsets = [
        (None,               {'fields': ['user','matricula','status']}),
        ('Studia', {'fields': ['numeryczna_l', 'dyskretna_l', 'program','semestr','ects', 'isim']}),
        ('Zapisy', {'fields': ['records_opening_bonus_minutes','block']}),
        ('Inne', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer','receive_mass_mail_grade','last_news_view'], 'classes': ['collapse']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program','status','semestr', 'isim')
    ordering = ['user__last_name','user__first_name']
    list_display_links = ('get_full_name',)
    list_max_show_all = 9999

    actions = [export_as_csv]

    def get_queryset(self, request):
       qs = super(StudentAdmin, self).get_queryset(request)
       return qs.select_related('program', 'program__type_of_points', 'user')

class ProgramAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
       qs = super(ProgramAdmin, self).get_queryset(request)
       return qs.select_related('type_of_points')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name','homepage','room','consultations',)
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None,               {'fields': ['user','status','homepage','room','consultations']}),
        ('Ogłoszenia mailowe', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer'], 'classes': ['collapse']}),
    ]
    ordering = ['user__last_name','user__first_name']
    list_display_links = ('get_full_name',)

    def get_queryset(self, request):
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


class ProfileInline(admin.StackedInline):
    model = UserProfile


class StudiaZamawianeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'points', 'comments')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricula', 'bank_account')
    ordering = ['student__user__last_name', 'student__user__first_name']

    def get_queryset(self, request):
        qs = super(StudiaZamawianeAdmin, self).get_queryset(request)
        return qs.select_related('student', 'student__user')


class StudiaZamawianeAdmin2012(admin.ModelAdmin):
    list_display = ('__unicode__', 'points', 'comments')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricula', 'bank_account')
    ordering = ['student__user__last_name', 'student__user__first_name']

    def get_queryset(self, request):
        qs = super(StudiaZamawianeAdmin2012, self).get_queryset(request)
        return qs.select_related('student', 'student__user')


class UserAdmin(DjangoUserAdmin):
    inlines = [StudentInline, ProfileInline, EmployeeInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'profile__is_student',
                   'profile__is_employee', 'profile__is_zamawiany')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(StudiaZamawiane, StudiaZamawianeAdmin)
admin.site.register(StudiaZamawiane2012, StudiaZamawianeAdmin2012)
admin.site.register(StudiaZamawianeMaileOpiekunow)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.users.models import Employee, Program, Student


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


class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'get_full_name', 'ects', 'program', 'semestr',)
    fieldsets = [
        (None, {'fields': ['user', 'matricula', 'is_active']}),
        ('Studia', {'fields': ['program', 'semestr', 'ects']}),
        ('Zapisy', {'fields': ['records_opening_bonus_minutes']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program', 'is_active', 'semestr')
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)
    list_max_show_all = 9999

    def get_queryset(self, request) -> QuerySet:
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.select_related('program', 'user')


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'homepage', 'room', 'consultations',)
    list_filter = ('user__is_active',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None,
         {'fields': ['user', 'homepage', 'room', 'consultations']})
    ]
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)

    def get_queryset(self, request) -> QuerySet:
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

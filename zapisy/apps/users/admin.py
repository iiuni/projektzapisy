import datetime

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models.opening_times import GroupOpeningTimes, T0Times

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

    actions = ['refresh_opening_times']

    def refresh_opening_times(self, request, queryset):
        """Refreshes opening times for selected students."""
        if queryset.count() < 1:
            self.message_user(request, "Nie wybrano studentow", level=messages.WARNING)
            return
        """The opening times refreshing concerns the upcoming semester"""

        semester = Semester.get_semester(Semester.get_current_semester().semester_ending + datetime.timedelta(days=1))

        if semester is None:
            self.message_user(request, "Aby uaktualnic czasy nalezy najpierw utworzyc przyszly semestr",
			      level=messages.WARNING)
            return
        if semester.records_opening is None:
            self.message_user(request, "Prosze uzupelnic szczegoly przyszlego semestru", level=messages.WARNING)
            return

        student: Student
        for student in queryset:
            T0Times.populate_t0_selected(semester, student)
            GroupOpeningTimes.populate_opening_times_selected(semester, student)
        self.message_user(request,
			  "Obliczono czasy otwarcia zapisów.",
			  level=messages.SUCCESS)

    refresh_opening_times.short_description = "Oblicz czasy otwarcia zapisów"


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

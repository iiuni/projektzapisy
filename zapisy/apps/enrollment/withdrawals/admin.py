"""Django Admin for director's withdrawal requests."""

from django.contrib import admin, messages

from . import services
from .models import DirectorWithdrawal, WithdrawalStatus


@admin.register(DirectorWithdrawal)
class DirectorWithdrawalAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'get_semester', 'status', 'created', 'decided_by', 'decided_at',
    )
    list_filter = ('status', 'course__semester')
    search_fields = (
        'student__user__first_name',
        'student__user__last_name',
        'student__matricula',
        'course__name',
    )
    readonly_fields = ('created', 'modified', 'decided_by', 'decided_at', 'status')
    raw_id_fields = ('student', 'course')

    fieldsets = [
        (None, {
            'fields': ['student', 'course', 'status'],
        }),
        ('Decyzja administratora', {
            'fields': ['admin_comment', 'decided_by', 'decided_at'],
        }),
        ('Daty', {
            'fields': ['created', 'modified'],
        }),
    ]

    actions = ['approve_selected', 'reject_selected']

    def get_semester(self, obj):
        return obj.course.semester
    get_semester.short_description = 'Semestr'
    get_semester.admin_order_field = 'course__semester'

    def approve_selected(self, request, queryset):
        """Approves selected PENDING withdrawal requests."""
        pending = queryset.filter(status=WithdrawalStatus.PENDING)
        if not pending.exists():
            self.message_user(
                request,
                'Żaden z wybranych wniosków nie jest w stanie oczekującym.',
                level=messages.WARNING,
            )
            return

        approved_count = 0
        errors = []
        for withdrawal in pending.select_related('student', 'course', 'course__semester'):
            try:
                services.approve_withdrawal(withdrawal, request.user)
                approved_count += 1
            except Exception as e:
                errors.append(f'{withdrawal}: {e}')

        if approved_count:
            self.message_user(
                request,
                f'Zatwierdzono {approved_count} wniosek/wniosków o wypis dyrektorski.',
                level=messages.SUCCESS,
            )
        for err in errors:
            self.message_user(request, f'Błąd: {err}', level=messages.ERROR)

    approve_selected.short_description = 'Zatwierdź wybrane wnioski'

    def reject_selected(self, request, queryset):
        """Rejects selected PENDING withdrawal requests."""
        pending = queryset.filter(status=WithdrawalStatus.PENDING)
        if not pending.exists():
            self.message_user(
                request,
                'Żaden z wybranych wniosków nie jest w stanie oczekującym.',
                level=messages.WARNING,
            )
            return

        rejected_count = 0
        errors = []
        for withdrawal in pending.select_related('student', 'course'):
            try:
                services.reject_withdrawal(withdrawal, request.user)
                rejected_count += 1
            except Exception as e:
                errors.append(f'{withdrawal}: {e}')

        if rejected_count:
            self.message_user(
                request,
                f'Odrzucono {rejected_count} wniosek/wniosków o wypis dyrektorski.',
                level=messages.SUCCESS,
            )
        for err in errors:
            self.message_user(request, f'Błąd: {err}', level=messages.ERROR)

    reject_selected.short_description = 'Odrzuć wybrane wnioski'

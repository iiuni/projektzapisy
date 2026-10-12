"""Django Admin for director's discharge requests."""

from django.contrib import admin, messages

from .models import DirectorDischarge, DischargeStatus


@admin.register(DirectorDischarge)
class DirectorDischargeAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'course', 'get_semester', 'status', 'created', 'get_decided_by', 'decided_at',
    )
    list_filter = ('status', 'course__semester')
    search_fields = (
        'student__user__first_name',
        'student__user__last_name',
        'student__matricula',
        'course__name',
    )
    readonly_fields = ('created', 'modified', 'get_decided_by', 'decided_at', 'status')
    raw_id_fields = ('student', 'course')

    fieldsets = [
        (None, {
            'fields': ['student', 'course', 'status'],
        }),
        ('Decyzja administratora', {
            'fields': ['admin_comment', 'get_decided_by', 'decided_at'],
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

    def get_decided_by(self, obj):
        if obj.decided_by is None and obj.status in (DischargeStatus.APPROVED, DischargeStatus.REJECTED):
            return 'Automatycznie'
        return obj.decided_by or '—'
    get_decided_by.short_description = 'Zatwierdził/Odrzucił'

    def approve_selected(self, request, queryset):
        """Approves selected PENDING discharge requests."""
        pending = queryset.filter(status=DischargeStatus.PENDING)
        if not pending.exists():
            self.message_user(
                request,
                'Żaden z wybranych wniosków nie jest w stanie oczekującym.',
                level=messages.WARNING,
            )
            return

        approved_count = 0
        errors = []
        for discharge in pending.select_related('student', 'course', 'course__semester'):
            try:
                discharge.approve(request.user)
                approved_count += 1
            except Exception as e:
                errors.append(f'{discharge}: {e}')

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
        """Rejects selected PENDING discharge requests."""
        pending = queryset.filter(status=DischargeStatus.PENDING)
        if not pending.exists():
            self.message_user(
                request,
                'Żaden z wybranych wniosków nie jest w stanie oczekującym.',
                level=messages.WARNING,
            )
            return

        rejected_count = 0
        errors = []
        for discharge in pending.select_related('student', 'course'):
            try:
                discharge.reject(request.user)
                rejected_count += 1
            except Exception as e:
                errors.append(f'{discharge}: {e}')

        if rejected_count:
            self.message_user(
                request,
                f'Odrzucono {rejected_count} wniosek/wniosków o wypis dyrektorski.',
                level=messages.SUCCESS,
            )
        for err in errors:
            self.message_user(request, f'Błąd: {err}', level=messages.ERROR)

    reject_selected.short_description = 'Odrzuć wybrane wnioski'

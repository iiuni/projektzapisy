from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib import messages

from apps.enrollment.courses.models.classroom import Classroom
from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester, Freeday, ChangedDay
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.courses.models.term import Term
from apps.enrollment.records.models import Record, RecordStatus, T0Times, GroupOpeningTimes


class GroupInline(admin.TabularInline):
    fields = ('id', 'teacher', 'get_terms_as_string', 'type', 'limit', 'extra', 'export_usos', 'usos_nr',)
    model = Group
    extra = 0
    readonly_fields = ('id', 'get_terms_as_string', 'usos_nr',)
    raw_id_fields = ("teacher",)
    show_change_link = True


class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')
    list_filter = ('building', 'capacity')


class SemesterAdmin(admin.ModelAdmin):

    list_display = ('get_name', 'visible')
    list_filter = ('visible', 'year', 'type')
    fieldsets = [
        (None, {'fields': ['year', 'type', 'visible']}),
        ('Ocena', {'fields': ['is_grade_active', 'first_grade_semester', 'second_grade_semester']}),
        ('Czas trwania semestru', {'fields': ['semester_beginning', 'semester_ending']}),
        ('Czas trwania zajęć', {'fields': ['lectures_beginning', 'lectures_ending']}),
        ('Czas trwania zapisów', {'fields': ['records_opening', 'records_ects_limit_abolition', 'records_ending', 'records_closing']}),
        ('Czas trwania dezyderat', {'fields': ['desiderata_opening', 'desiderata_closing']}),
    ]
    list_editable = ('visible',)

    actions = ['refresh_opening_times']

    def refresh_opening_times(self, request, queryset):
        """Computes Opening times for all students."""
        if queryset.count() != 1:
            self.message_user(request, "Trzeba wybrać pojedynczy semestr!", level=messages.ERROR)
            return
        semester = queryset.get()
        T0Times.populate_t0(semester)
        GroupOpeningTimes.populate_opening_times(semester)
        self.message_user(request,
                          f"Obliczono czasy otwarcia zapisów dla semestru {semester}.",
                          level=messages.SUCCESS)

    refresh_opening_times.short_description = "Oblicz czasy otwarcia zapisów"


class FreedayAdmin(admin.ModelAdmin):
    # todo: add filter with academic_year with newer django
    ordering = ('-day',)


class EffectsListFilter(SimpleListFilter):
    title = 'Grupa efektów kształcenia'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'effects'

    def lookups(self, request, model_admin):
        result = []
        for effect in Effects.objects.all():
            result.append((str(effect.id), effect))

        return result

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(effects=self.value())
        else:
            return queryset


class TermInline(admin.TabularInline):
    model = Term
    extra = 0


class RecordInline(admin.TabularInline):
    model = Record
    extra = 0
    fields = ('student', 'status',)
    raw_id_fields = ('student',)
    can_delete = False

    def get_queryset(self, request):
        """Only shows enrolled and queued students.

        They will be showed enrolled first, then queued ones, ordered by the
        enqueuing time.
        """
        qs = super().get_queryset(request)
        return qs.exclude(status=RecordStatus.REMOVED).order_by('-status', 'created')


class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = (
        'id',
        'course',
        'teacher',
        'type',
        'limit',
        'get_terms_as_string')
    list_filter = ('type', 'course__semester', 'teacher')
    search_fields = (
        'teacher__user__first_name',
        'teacher__user__last_name',
        'course__name')
    inlines = [
        TermInline, RecordInline
    ]

    raw_id_fields = ('course', 'teacher')

    def changelist_view(self, request, extra_context=None):

        if 'course__semester__id__exact' not in request.GET:

            q = request.GET.copy()
            semester = Semester.get_current_semester()
            q['course__semester__id__exact'] = semester.id
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(GroupAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super(GroupAdmin, self).get_queryset(request)
        return qs.select_related('teacher', 'teacher__user', 'course',
                                 'course__semester').prefetch_related('term', 'record_set')


@admin.register(CourseInstance)
class CourseInstanceAdmin(admin.ModelAdmin):
    list_filter = ('semester', 'course_type', ('owner', admin.RelatedOnlyFieldListFilter),
                   'tags', 'effects',)
    list_display = ('name', 'owner', 'course_type', 'semester',)
    search_fields = ('name', 'name_en')
    ordering = ('semester', 'owner', 'offer')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('owner', 'semester', 'offer')

    inlines = [GroupInline, ]


class TypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'meta_type')
    list_filter = ('group', 'meta_type')


admin.site.register(Group, GroupAdmin)
admin.site.register(Tag)
admin.site.register(Effects)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Freeday, FreedayAdmin)
admin.site.register(ChangedDay)
admin.site.register(Type, TypeAdmin)

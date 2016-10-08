# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.db.models.query import EmptyQuerySet
from django.forms import ModelForm
from modeltranslation.admin import TranslationAdmin

from apps.enrollment.courses.models import *
from apps.enrollment.records.models import Record, STATUS_REMOVED, STATUS_ENROLLED, Queue


class GroupInline(admin.TabularInline):
    model = Group
    extra = 0
    raw_id_fields = ("teacher",)


class CourseForm(ModelForm):

    class Meta:
        model = Course

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['information'].queryset = CourseDescription.objects.filter(entity=kwargs['instance'].entity)\
                .select_related('entity')
        else:
            self.fields['information'].queryset = EmptyQuerySet()


class CourseEntityForm(ModelForm):

    class Meta:
        model = CourseEntity

    def __init__(self, *args, **kwargs):
        super(CourseEntityForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['information'].queryset = CourseDescription.objects.filter(entity=kwargs['instance']).select_related('entity')
        else:
            self.fields['information'].queryset = EmptyQuerySet()


class CourseAdmin(admin.ModelAdmin):
    list_display =('entity', 'semester',)
    list_filter = ('semester',)
    search_fields = ('entity__name',)
    fieldsets = [
        (None,               {'fields': ['entity'], 'classes': ['long_name']}),
        (None, {'fields': ['information', 'english']}),
        ('Szczegóły', {'fields': ['records_start', 'records_end', 'teachers','semester','slug','web_page'], 'classes': ['collapse']}),
    ]
    inlines = [GroupInline, ]

    form = CourseForm


    def changelist_view(self, request, extra_context=None):

        if not request.GET.has_key('semester__id__exact'):

            q = request.GET.copy()
            semester = Semester.get_current_semester()
            q['semester__id__exact'] = semester.id
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(CourseAdmin,self).changelist_view(request, extra_context=extra_context)

    def get_object(self, request, object_id):
        """
        Returns an instance matching the primary key provided. ``None``  is
        returned if no match is found (or the object_id failed validation
        against the primary key field).
        """
        queryset = self.queryset(request)
        model = queryset.model
        try:
            object_id = model._meta.pk.to_python(object_id)
            return queryset.select_related('semester').get(pk=object_id)
        except (model.DoesNotExist, ValidationError):
            return None

    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(CourseAdmin, self).queryset(request)
       return qs.select_related('semester', 'type')

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')
    list_filter = ('building','capacity')

class SemesterAdmin(admin.ModelAdmin):

    list_display = ('get_name', 'visible')
    list_filter = ('visible','year','type')
    fieldsets = [
        (None,               {'fields': ['year','type','visible']}),
        ('Ocena', {'fields': ['is_grade_active', 'first_grade_semester', 'second_grade_semester']}),
        ('Czas trwania semestru', {'fields': ['semester_beginning','semester_ending']}),
        ('Czas trwania zajęć', {'fields': ['lectures_beginning','lectures_ending']}),
        ('Czas trwania zapisów', {'fields': ['records_opening','records_ects_limit_abolition','records_closing']}),
        ('Czas trwania dezyderat', {'fields': ['desiderata_opening', 'desiderata_closing']}),
    ]
    list_editable = ('visible',)

class CourseInline(admin.TabularInline):
    model = Course


class PointsInline(admin.TabularInline):
    model = PointsOfCourseEntities
    extra = 0

class TagsInline(admin.TabularInline):
    model = TagCourseEntity
    extra=0


class EffectsListFilter(SimpleListFilter):
    title = u'Grupa efektów kształcenia'

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


class CourseEntityAdmin(TranslationAdmin):
    list_display = ('name', 'shortName', 'owner')
    search_fields = ('name', 'shortName', 'owner__user__first_name', 'owner__user__last_name' )
    fieldsets = [
        (None,               {'fields': ['name','shortName','type', 'information'], 'classes': ['long_name']}),
        (None,               {'fields': ['owner', 'status', 'semester', 'effects']}),
        (u'Godziny', {'fields': ['lectures', 'exercises', 'laboratories', 'repetitions', 'seminars', 'exercises_laboratiories']}),
        (u'Zmiana sposobu liczenia punktów',               {'fields': ['algorytmy_l', 'dyskretna_l', 'numeryczna_l', 'programowanie_l']}),
        (None,               {'fields': ['ue', 'english', 'exam', 'suggested_for_first_year', 'deleted']}),
        ('USOS',             {'fields': ['usos_kod'], 'classes': ['collapse']}),

    ]
    list_filter = ('semester',  'status', 'type', EffectsListFilter, 'owner')
    form = CourseEntityForm

    inlines = [PointsInline, TagsInline]

    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(CourseEntityAdmin, self).queryset(request)
       return qs.select_related('owner', 'owner__user', 'type')

class TermInline(admin.TabularInline):
    model = Term
    extra = 0

class RecordInlineForm(ModelForm):
    class Meta:
        model = Record

    # def save(self, commit=True):
    #
    #     record = super(RecordInlineForm, self).save(commit=False)
    #
    #     if record.id:
    #         old = Record.objects.get(id=record.id)
    #         if old.status <> record.status:
    #             if record.status == STATUS_REMOVED:
    #                 record.group.remove_from_enrolled_counter(record.student)
    #                 Group.do_rearanged(record.group)
    #             elif  record.status == STATUS_ENROLLED:
    #                 record.group.add_to_enrolled_counter(record.student)
    #                 Queue.objects.filter(group=record.group, student=record.student, deleted=False).update(deleted=True)
    #                 record.group.queued = Queue.objects.filter(group=record.group, deleted=False).count()
    #                 record.group.save()
    #
    #     else:
    #         if record.status == STATUS_REMOVED:
    #             pass
    #         elif  record.status == STATUS_ENROLLED:
    #             record.group.add_to_enrolled_counter(record.student)
    #             Queue.objects.filter(group=record.group, student=record.student, deleted=False).update(deleted=True)
    #             record.group.queued = Queue.objects.filter(group=record.group, deleted=False).count()
    #             record.group.save()
    #
    #     if commit:
    #         record.save()
    #
    #     return record


class RecordInline(admin.TabularInline):
    model = Record
    extra = 0
    readonly_fields = ('id', 'student', 'status')
    can_delete = False

class QueuedInlineForm(ModelForm):
    class Meta:
        model = Queue

    # def save(self, commit=True):
    #     queue = super(QueuedInlineForm, self).save(commit=False)
    #
    #
    #     if queue.id:
    #         old = Queue.objects.get(id=queue.id)
    #         if not old.deleted and queue.deleted:
    #             queue.group.remove_from_queued_counter(queue.student)
    #         elif old.deleted and not queue.deleted:
    #             queue.group.add_to_queued_counter(queue.student)
    #     else:
    #         if not queue.deleted:
    #             queue.group.add_to_queued_counter(queue.student)
    #
    #     if commit:
    #         queue.save()
    #
    #     return queue

class QueuedInline(admin.TabularInline):
    model = Queue
    extra = 0
    raw_id_fields = ("student",)

    can_delete = False
    form = QueuedInlineForm



class GroupAdmin(admin.ModelAdmin):
    readonly_fields = ('limit', 'id')
    list_display = ('id', 'course', 'teacher','type','limit','limit_zamawiane','limit_zamawiane2012', 'limit_isim', 'get_terms_as_string')
    list_filter = ('type', 'course__semester', 'teacher')
    search_fields = ('teacher__user__first_name','teacher__user__last_name','course__entity__name')
    inlines = [
        TermInline,RecordInline, QueuedInline
    ]


    raw_id_fields = ('course', 'teacher')

    def response_add(self, request, new_object, post_url_continue='../%s/'):
        obj = self.after_saving_model_and_related_inlines(new_object)
        return super(GroupAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        obj = self.after_saving_model_and_related_inlines(obj)
        return super(GroupAdmin, self).response_change(request, obj)

    def save_model(self, request, obj, form, change):

        if obj.pk:
            rearrange = obj.queued > 0 and obj.enrolled < obj.limit
            old = Group.objects.get(pk=obj.pk)
            rearrange = rearrange and (obj.limit_isim != old.limit_isim or obj.limit_zamawiane != old.limit_zamawiane or
                                       obj.limit_zamawiane2012 != old.limit_zamawiane2012 or obj.limit != old.limit)
            if rearrange:
                from ...records.utils import run_rearanged
                for _ in range(obj.limit - obj.enrolled):
                    run_rearanged(None, obj)

        obj.save()

    def after_saving_model_and_related_inlines(self, obj):
        from apps.enrollment.courses.models import Term as T
        from apps.schedule.models import Event, Term
        # Perform extra operation after all inlines are saved

        Event.objects.filter(group=obj, type='3').delete()
        semester = obj.course.semester

        freedays = Freeday.objects.filter(Q(day__gte=semester.lectures_beginning),
                                          Q(day__lte=semester.lectures_ending))\
                          .values_list('day', flat=True)
        changed = ChangedDay.objects.filter(Q(day__gte=semester.lectures_beginning), Q(day__lte=semester.lectures_ending)).values_list('day', 'weekday')
        terms = T.objects.filter(group=obj).select_related('group', 'group__course', 'group__course__courseentity')
        days = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        day = semester.lectures_beginning

        while day <= semester.lectures_ending:

            if day in freedays:
                day = day + timedelta(days=1)
                continue

            weekday = day.weekday()

            for d in changed:
                if d[0] == day:
                    weekday = int(d[1]) - 1
                    break

            days[weekday].append(day)

            day = day + timedelta(days=1)

        for t in terms:
            ev = Event()
            ev.group = obj
            ev.course = t.group.course
            ev.title = ev.course.entity.get_short_name()
            ev.type = '3'
            ev.visible = True
            ev.status = '1'
            if obj.teacher:
                ev.author_id = obj.teacher.user.id
            else:
                ev.author_id = 1
            ev.save()

            for room in t.classrooms.all():
                for day in days[int(t.dayOfWeek) - 1]:
                    newTerm = Term()
                    newTerm.event = ev
                    newTerm.day = day
                    newTerm.start = timedelta(hours=t.start_time.hour, minutes=t.start_time.minute)
                    newTerm.end = timedelta(hours=t.end_time.hour, minutes=t.end_time.minute)
                    newTerm.room = room
                    newTerm.save()

        return obj

    def changelist_view(self, request, extra_context=None):

        if not request.GET.has_key('course__semester__id__exact'):

            q = request.GET.copy()
            semester = Semester.get_current_semester()
            q['course__semester__id__exact'] = semester.id
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(GroupAdmin,self).changelist_view(request, extra_context=extra_context)

    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(GroupAdmin, self).queryset(request)
       return qs.select_related('teacher', 'teacher__user', 'course', 'course__semester', 'course__type').prefetch_related('term')

    class Media:
        css = {
            "all": ("css/admin/group.css",)
        }
        js = ("js/admin/group.js",)


class TypeAdmin(admin.ModelAdmin):
    list_display = ('name','group','meta_type')
    list_filter = ('group','meta_type')





class CourseDescriptionAdmin(TranslationAdmin):
    list_display = ('entity','created', 'author',)
    search_fields = ('entity__name',)
    list_filter = ('entity__type',)

    save_as = True

    def save_model(self, request, obj, form, change):
        obj.author = request.user.employee
        obj.save()
        entity = obj.entity
        entity.information = obj
        entity.save()


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseDescription, CourseDescriptionAdmin)
admin.site.register(CourseEntity, CourseEntityAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Tag)
admin.site.register(Effects)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Freeday)
admin.site.register(ChangedDay)
admin.site.register(Type, TypeAdmin)
admin.site.register(PointTypes)
admin.site.register(PointsOfCourseEntities)

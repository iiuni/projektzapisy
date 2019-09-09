from django.contrib.auth.decorators import permission_required
from django.db import models
from django.shortcuts import render

from apps.enrollment.records.models import RecordStatus
from apps.users.models import Student
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group


@permission_required('courses.view_stats')
def students(request):
    semester = Semester.objects.get_next()
    t0_time_agg = models.Min('t0times__time', filter=models.Q(t0times__semester=semester))
    group_opening_agg = models.Min(
        'groupopeningtimes__time',
        filter=models.Q(groupopeningtimes__group__course__semester=semester))
    students = Student.get_active_students().select_related('user').annotate(
        min_t0=t0_time_agg).annotate(
            min_opening_time=group_opening_agg).order_by('min_opening_time')
    return render(request, 'statistics/students_list.html', {
        'students': students,
    })


@permission_required('courses.view_stats')
def groups(request):
    semester = Semester.objects.get_next()
    enrolled_agg = models.Count(
        'record', filter=models.Q(record__status=RecordStatus.ENROLLED), distinct=True)
    queued_agg = models.Count(
        'record', filter=models.Q(record__status=RecordStatus.QUEUED), distinct=True)
    pinned_agg = models.Count('pin', distinct=True)

    groups = Group.objects.filter(course__semester=semester).select_related(
        'course', 'teacher', 'teacher__user').order_by('course', 'type').only(
            'course__name', 'teacher__user__first_name', 'teacher__user__last_name', 'limit',
            'type').annotate(enrolled=enrolled_agg).annotate(queued=queued_agg).annotate(
                pinned=pinned_agg)
    return render(request, 'statistics/groups_list.html', {
        'groups': groups,
    })

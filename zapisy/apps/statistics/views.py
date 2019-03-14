from django.contrib.auth.decorators import permission_required
from django.db import models
from django.template.response import TemplateResponse

from apps.enrollment.records.models import Record, RecordStatus, GroupOpeningTimes, T0Times
from apps.users.models import Student
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course import CourseEntity, Course


@permission_required('courses.view_stats')
def main(request):
    return TemplateResponse(request, 'statistics/base.html')


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
    return TemplateResponse(request, 'statistics/students_list.html', {
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
        'course', 'teacher', 'teacher__user', 'course__entity').order_by('course').annotate(
            enrolled=enrolled_agg).annotate(queued=queued_agg).annotate(pinned=pinned_agg)
    return TemplateResponse(request, 'statistics/groups_list.html', {
        'groups': groups,
    })


@permission_required('courses.view_stats')
def votes(request):
    proposals = CourseEntity.statistics.in_year()
    return TemplateResponse(request, 'statistics/votes.html', locals())


@permission_required('courses.view_stats')
def swap(request):
    semester = Semester.objects.get_next()
    courses = Course.objects.filter(semester=semester).select_related('entity')

    types = [('2', 'ćwiczenia'), ('3', 'pracownia'),
             ('5', 'ćwiczenio-pracownia'), ('6', 'seminarium'),
             ('10', 'projekt')]

    for course in courses:
        course.groups_items = []

        for type in types:
            groups = Group.objects.filter(
                course=course, type=type[0]).select_related(
                    'course', 'course__entity', 'teacher')
            queues = {}
            students = {}
            lists = {}
            used = []

            for g in groups:
                lists[g.id] = []
                queues[g.id] = []
                for r in Record.objects.filter(group=g).exclude(
                        status=RecordStatus.REMOVED).select_related('student', 'student__user'):
                    if r.status == RecordStatus.ENROLLED:
                        lists[g.id].append(r.student)
                        students[r.student_id] = g
                    elif r.status == RecordStatus.QUEUED:
                        queues[g.id].append(r.student)

            for group in groups:
                group.swaps = []
                queue = queues[group.id]
                for s in queue:
                    if s.id in students:
                        for sp in lists[group.id]:
                            if students[
                                    sp.
                                    id] == group and sp.id not in used and sp in queues[
                                        students[s.id].id]:
                                used.append(sp.id)
                                group.swaps.append({
                                    'student_in_queue': s,
                                    'student_in_group': sp,
                                    'to': students[s.id]
                                })
                                break
                course.groups_items.append(group)

    return TemplateResponse(request, 'statistics/swap.html', locals())

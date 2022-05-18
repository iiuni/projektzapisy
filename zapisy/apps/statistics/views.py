from collections import defaultdict

from django.contrib.auth.decorators import permission_required
from django.db import models
from django.shortcuts import render
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.templatetags.course_types import decode_class_type_plural
from apps.enrollment.records.models import RecordStatus
from apps.enrollment.records.models.records import Record
from apps.users.models import Student


@permission_required('courses.view_stats')
def students(request):
    semester = Semester.get_upcoming_semester()
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
    semester = Semester.get_upcoming_semester()
    enrolled_agg = models.Count(
        'record', filter=models.Q(record__status=RecordStatus.ENROLLED), distinct=True)
    queued_agg = models.Count(
        'record', filter=models.Q(record__status=RecordStatus.QUEUED), distinct=True)
    pinned_agg = models.Count('pin', distinct=True)

    groups = Group.objects.filter(course__semester=semester).select_related(
        'course', 'teacher', 'teacher__user').order_by('course', 'type').only(
        'course__name', 'teacher__user__first_name', 'teacher__user__last_name', 'limit',
        'type').prefetch_related('guaranteed_spots', 'guaranteed_spots__role').annotate(
        enrolled=enrolled_agg).annotate(queued=queued_agg).annotate(pinned=pinned_agg)
    waiting_students = Record.list_waiting_students(
        CourseInstance.objects.filter(semester=semester))

    courses = defaultdict(list)
    for group in groups:
        courses[group.course.id].append(group)

    sorted_courses_ids = sorted(courses, key=lambda item: courses[item][0].course.name, reverse=True)
    courses_list = []

    for i, course_id in enumerate(sorted_courses_ids):
        course_groups = []
        course_name = ""
        for group in courses[course_id]:
            course_groups.append({
                'id': group.id,
                'teacher_name': group.teacher.get_full_name(),
                'type_name': group.get_type_display(),
                'limit': group.limit,
                'enrolled': group.enrolled,
                'queued': group.queued,
                'pinned': group.pinned,
                'guaranteed_spots': [{'name': gs.role.name, 'limit': gs.limit}
                                     for gs in group.guaranteed_spots.all()],
                'url': reverse('admin:courses_group_change', None, [str(group.id)])
            })
            course_name = group.course.name

        waiting_by_class_type = [{'name': decode_class_type_plural(class_type),
                                  'number': waiting_students[course_id][class_type]}
                                 for class_type in waiting_students[course_id]]

        courses_list.append({
            'id': course_id,
            'alphabetical_sorting_index': i,
            'course_name': course_name,
            'groups': course_groups,
            'waiting_students': waiting_by_class_type,
            'max_of_waiting_students': max([s['number'] for s in waiting_by_class_type], default=0)
        })

    return render(request, 'statistics/groups_list.html', {
        'courses_list': courses_list
    })

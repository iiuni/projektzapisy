import locale
from typing import Dict, Optional, Tuple

from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.utils import mailto
from apps.users.decorators import employee_required
from apps.users.models import Student
from zapisy.apps.enrollment.courses import utils

locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")


def courses_list(request, semester_id: Optional[int] = None):
    """A basic courses view with courses listed on the right and no course selected."""
    semester: Optional[Semester]
    if semester_id is None:
        semester = Semester.get_upcoming_semester()
    else:
        semester = get_object_or_404(Semester, pk=semester_id)
    data = utils.prepare_courses_list_data(semester)
    return render(
        request, 'courses/courses.html', data)


def course_view_data(request, slug) -> Tuple[Optional[CourseInstance], Optional[Dict]]:
    """Retrieves course and relevant data for the request.

    If course does not exist it returns two None objects.
    """
    course: CourseInstance
    try:
        course = CourseInstance.objects.filter(slug=slug).select_related(
            'semester', 'course_type').prefetch_related('tags', 'effects').get()
    except CourseInstance.DoesNotExist:
        return None, None

    student: Optional[Student] = None
    if request.user.is_authenticated and request.user.student:
        student = request.user.student

    groups = course.groups.select_related(
        'teacher', 'teacher__user',
    ).prefetch_related(
        'term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role'
    ).annotate(
        earliest_dayOfWeek=Min('term__dayOfWeek'), earliest_start_time=Min('term__start_time')
    ).order_by(
        'earliest_dayOfWeek', 'earliest_start_time', 'teacher__user__last_name', 'teacher__user__first_name'
        )

    # Collect the general groups statistics.
    groups_stats = Record.groups_stats(groups)
    # Collect groups information related to the student.
    groups = Record.is_recorded_in_groups(student, groups)
    student_can_enqueue = Record.can_enqueue_groups(
        student, course.groups.all())
    student_can_dequeue = Record.can_dequeue_groups(
        student, course.groups.all())

    for group in groups:
        group.num_enrolled = groups_stats.get(group.pk).get('num_enrolled')
        group.num_enqueued = groups_stats.get(group.pk).get('num_enqueued')
        group.can_enqueue = student_can_enqueue.get(group.pk)
        group.can_dequeue = student_can_dequeue.get(group.pk)

    teachers = {g.teacher for g in groups}

    course.is_enrollment_on = any(g.can_enqueue for g in groups)

    waiting_students = {}
    if request.user.employee:
        waiting_students = Record.list_waiting_students([course])[course.id]

    data = {
        'course': course,
        'teachers': teachers,
        'groups': groups,
        'waiting_students': waiting_students,
    }
    return course, data


def course_view(request, slug):
    course, data = course_view_data(request, slug)
    if course is None:
        raise Http404
    data.update(utils.prepare_courses_list_data(course.semester))
    return render(request, 'courses/courses.html', data)


@login_required
def course_list_view(request, course_slug: str, class_type: int = None):
    course, _, groups_ids = utils.get_all_group_ids_for_course_slug(course_slug, class_type=class_type)
    if course is None:
        raise Http404("Kurs o podanym identyfikatorze nie istnieje.")
    groups_data_enrolled = utils.get_group_data(groups_ids, request.user, status=RecordStatus.ENROLLED)
    groups_data_queued = utils.get_group_data(groups_ids, request.user, status=RecordStatus.QUEUED)

    students_in_course, students_in_queue = utils.get_students_from_data(
        groups_data_enrolled, groups_data_queued
    )
    can_user_see_all_students_here = any(
        [
            group["can_user_see_all_students_here"]
            for group in groups_data_enrolled.values()
        ]
    ) or any(
        [
            group["can_user_see_all_students_here"]
            for group in groups_data_queued.values()
        ]
    )

    data = {
            'students_in_course': students_in_course,
            'students_in_queue': students_in_queue,
            'course': course,
            'can_user_see_all_students_here': can_user_see_all_students_here,
            'mailto_group': mailto(request.user, students_in_course, bcc=False),
            'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
            'mailto_group_bcc': mailto(request.user, students_in_course, bcc=True),
            'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
            'class_type': class_type,
    }
    data.update(utils.prepare_courses_list_data(course.semester))
    return render(request, 'courses/course_list.html', data)


@login_required
def group_view(request, group_id):
    """Group records view.

    Presents list of all students enrolled and enqueued to group.
    """
    enrolled_data = utils.get_group_data([group_id], request.user, status=RecordStatus.ENROLLED)
    queued_data = utils.get_group_data([group_id], request.user, status=RecordStatus.QUEUED)
    students_in_group, students_in_queue = utils.get_students_from_data(
        enrolled_data, queued_data, preserve_queue_ordering=True
    )
    group: Group = enrolled_data[group_id].get("group")

    data = {
        'students_in_group': students_in_group,
        'students_in_queue': students_in_queue,
        'guaranteed_spots': enrolled_data.get('guaranteed_spots_rules'),
        'group': group,
        'can_user_see_all_students_here': enrolled_data[group_id].get("can_user_see_all_students_here"),
        'mailto_group': mailto(request.user, students_in_group, bcc=False),
        'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
        'mailto_group_bcc': mailto(request.user, students_in_group, bcc=True),
        'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    }
    data.update(utils.prepare_courses_list_data(group.course.semester))
    return render(request, 'courses/group.html', data)


@employee_required
def group_enrolled_csv(request, group_id):
    """Prints out the group members in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return utils.recorded_students_csv([group_id], RecordStatus.ENROLLED, request.user)


@employee_required
def group_queue_csv(request, group_id):
    """Prints out the group queue in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return utils.recorded_students_csv([group_id], RecordStatus.QUEUED, request.user, preserve_ordering=True)


@employee_required
def course_enrolled_csv(request, course_slug):
    """Prints out the course members in csv format."""
    _, course_short_name, group_ids = utils.get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    return utils.recorded_students_csv(group_ids, RecordStatus.ENROLLED, request.user, course_short_name)


@employee_required
def course_queue_csv(request, course_slug):
    """Prints out the course queue in csv format."""
    _, course_short_name, group_ids = utils.get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    group_data = utils.get_group_data(group_ids, request.user, status=RecordStatus.ENROLLED)

    students_enrolled = set()
    for group in group_data.values():
        students_enrolled.update(group.get("students", []))

    return utils.recorded_students_csv(
        group_ids,
        RecordStatus.QUEUED,
        request.user,
        course_short_name,
        exclude_students=students_enrolled
    )

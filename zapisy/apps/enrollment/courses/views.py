import csv
import json
from typing import Tuple, Optional, Dict, List

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.tag import Tag
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.utils import mailto
from apps.users.decorators import employee_required
from apps.users.models import BaseUser, Student


def get_course_list_info_for_semester(semester):
    """Builds a list of courses in the semester to show on the right side.
    """
    courses = CourseInstance.objects.filter(
        semester=semester
    ).order_by('name').select_related('owner').prefetch_related('effects', 'tags')
    semester_for_json = {
        'id': semester.pk,
        'year': semester.year,
        'type': semester.get_type_display(),
    }
    courses_list_info = {
        'courseList': [c.__json__() for c in courses],
        'semesterInfo': semester_for_json,
    }
    return courses_list_info


def prepare_courses_list_to_render(request, semester=None):
    ''' generates template data for filtering and list of courses '''
    if not semester:
        semester = Semester.objects.get_next()
    semesters = Semester.objects.filter(visible=True)
    courses_list_json = json.dumps(get_course_list_info_for_semester(semester))
    return {
        'courses_list_json': courses_list_json,
        'semester_courses': semesters,
        'types_list': Type.get_all_for_jsfilter(),
        'default_semester': semester,
        'effects': Effects.objects.all(),
        'tags': Tag.objects.all(),
    }


def courses_list(request):
    """A basic courses view with courses listed on the right and no course selected.
    """
    return render(request, 'courses/courses_list.html', prepare_courses_list_to_render(request))


def semester_info(request, semester_id):
    """Provides courses list for a given semester."""
    semester: Semester = None
    try:
        semester = Semester.objects.get(pk=semester_id)
    except Semester.DoesNotExist:
        raise Http404
    if not semester.visible:
        raise Http404
    courses_list = get_course_list_info_for_semester(semester)
    return JsonResponse(courses_list)


def course_view_data(request, slug) -> Tuple[Optional[CourseInstance], Optional[Dict]]:
    """Retrieves course and relevant data for the request.

    If course does not exist it returns two None objects.
    """
    course: CourseInstance = None
    try:
        course = CourseInstance.objects.filter(slug=slug).select_related(
            'semester', 'course_type').prefetch_related('tags', 'effects').get()
    except CourseInstance.DoesNotExist:
        return None, None

    student: Student = None
    if request.user.is_authenticated and BaseUser.is_student(request.user):
        student = request.user.student

    groups = course.groups.exclude(extra='hidden').select_related(
        'teacher',
        'teacher__user',
    ).prefetch_related('term', 'term__classrooms')

    # Collect the general groups statistics.
    groups_stats = Record.groups_stats(groups)
    # Collect groups information related to the student.
    student_status_groups = Record.is_recorded_in_groups(student, groups)
    student_can_enqueue = Record.can_enqueue_groups(student, course.groups.all())
    student_can_dequeue = Record.can_dequeue_groups(student, course.groups.all())

    for group in groups:
        group.num_enrolled = groups_stats.get(group.pk).get('num_enrolled')
        group.num_enqueued = groups_stats.get(group.pk).get('num_enqueued')
        group.is_enrolled = student_status_groups.get(group.pk).get('enrolled')
        group.is_enqueued = student_status_groups.get(group.pk).get('enqueued')
        group.priority = student_status_groups.get(group.pk).get('priority')
        group.can_enqueue = student_can_enqueue.get(group.pk)
        group.can_dequeue = student_can_dequeue.get(group.pk)

    teachers = {g.teacher for g in groups}

    course.is_enrollment_on = any(g.can_enqueue for g in groups)

    data = {
        'course': course,
        'teachers': teachers,
        'groups': groups,
        'grouped_waiting_students': get_grouped_waiting_students(course, request.user)
    }
    return course, data


def course_ajax(request, slug):
    """Produces solely the inner frame of the course page.

    The inner frame and some additional data is wrapped into the JSON response
    to be put in place by JS. This allows to only load a part of the page.
    """
    course, data = course_view_data(request, slug)
    if course is None:
        raise Http404
    rendered_html = render_to_string('courses/course_info.html', data, request)
    return JsonResponse({
        'courseHtml': rendered_html,
        'courseName': course.name,
    })


def course_view(request, slug):
    course, data = course_view_data(request, slug)
    if course is None:
        raise Http404
    data.update(prepare_courses_list_to_render(request, course.semester))
    return render(request, 'courses/course.html', data)


def can_user_view_students_list_for_group(user: BaseUser, group: Group) -> bool:
    """Tell whether the user is authorized to see students' names
    and surnames in the given group.
    """
    is_user_proper_employee = (
        BaseUser.is_employee(user) and not BaseUser.is_external_contractor(user)
    )
    is_user_group_teacher = user == group.teacher.user
    return is_user_proper_employee or is_user_group_teacher


@login_required
def group_view(request, group_id):
    """Group records view - list of all students enrolled and enqueued to group.
    """
    group: Group = None
    try:
        group = Group.objects.select_related(
            'course', 'course__semester', 'teacher', 'teacher__user'
        ).prefetch_related('term', 'term__classroom').get(id=group_id)
    except Group.DoesNotExist:
        raise Http404

    records = Record.objects.filter(
        group_id=group_id).exclude(status=RecordStatus.REMOVED).select_related(
            'student', 'student__user', 'student__program', 'student__consent').order_by('created')
    students_in_group = []
    students_in_queue = []
    record: Record
    for record in records:
        if record.status == RecordStatus.ENROLLED:
            students_in_group.append(record.student)
        elif record.status == RecordStatus.QUEUED:
            students_in_queue.append(record.student)
    data = prepare_courses_list_to_render(request)
    data.update({
        'students_in_group': students_in_group,
        'students_in_queue': students_in_queue,
        'group': group,
        'can_user_see_all_students_here': can_user_view_students_list_for_group(
            request.user, group),
        'mailto_group': mailto(request.user, students_in_group, bcc=False),
        'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
        'mailto_group_bcc': mailto(request.user, students_in_group, bcc=True),
        'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    })
    return render(request, 'courses/group.html', data)


def recorded_students_csv(group_id: int, status: RecordStatus) -> HttpResponse:
    """Builds the HttpResponse with list of student enrolled/enqueued in group.
    """
    order = 'student__user__last_name' if status == RecordStatus.ENROLLED else 'created'
    records_in_group = Record.objects.filter(
        group_id=group_id, status=status
    ).select_related('student', 'student__user').order_by(order)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="group-{}-{}.csv"'.format(
        group_id, status.display
    )

    writer = csv.writer(response)
    for record in records_in_group:
        student = record.student
        writer.writerow([
            student.user.first_name, student.user.last_name, student.matricula, student.user.email
        ])
    return response


@employee_required
def group_enrolled_csv(request, group_id):
    """Prints out the group members in csv format."""
    try:
        _ = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        raise Http404
    return recorded_students_csv(group_id, RecordStatus.ENROLLED)


@employee_required
def group_queue_csv(request, group_id):
    """Prints out the group queue in csv format."""
    try:
        _ = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        raise Http404
    return recorded_students_csv(group_id, RecordStatus.QUEUED)


def get_grouped_waiting_students(course: CourseInstance, user) -> List:
    """Return numbers of waiting students grouped by course group type.

    The user argument is used to decide if the list should be generated at all.
    """
    if not user.is_superuser:
        return []

    group_types: List = [
        {'id': '2', 'name': 'cwiczenia'},
        {'id': '3', 'name': 'pracownie'},
        {'id': '5', 'name': 'ćwiczenio-pracownie'}
    ]

    return [{
        'students_amount': Record.get_number_of_waiting_students(course, group_type['id']),
        'type_name': group_type['name']
    } for group_type in group_types]

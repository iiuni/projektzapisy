import csv
import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from apps.enrollment.courses.models.course import Course
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
    courses = (
        Course.visible.filter(semester=semester).order_by('entity__name').select_related(
            'entity', 'entity__type'
        ).prefetch_related('entity__effects', 'entity__tags', 'entity__owner')
    )
    courses_list_for_json = [c.serialize_for_json() for c in courses]
    semester_for_json = {
        "id": semester.pk,
        "year": semester.year,
        "type": semester.get_type_display()
    }
    courses_list_info = {"courseList": courses_list_for_json, "semesterInfo": semester_for_json}
    return courses_list_info


def prepare_courses_list_to_render(request, semester=None):
    ''' generates template data for filtering and list of courses '''
    if not semester:
        semester = Semester.get_default_semester()
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


def course_view(request, slug):
    """Presents a single course to the viewer.

    The view will show all the groups associated with this course. If the viewer
    is a student authorized to participate in enrollment into these groups, the
    view is just for that..
    """
    course: Course = None
    try:
        course = (
            Course.objects.filter(slug=slug).select_related('semester', 'entity', 'entity__type')
            .prefetch_related('groups', 'entity__tags', 'entity__effects').get()
        )
    except Course.DoesNotExist:
        return Http404

    student: Student = None
    if request.user.is_authenticated and BaseUser.is_student(request.user):
        student = request.user.student

    groups = course.groups.all().select_related(
        'teacher',
        'teacher__user',
    ).prefetch_related('term', 'term__classrooms')
    group_ids = {g.id for g in groups}

    # Collect the general groups statistics.
    groups_stats = Record.groups_stats(group_ids)
    # Collect groups information related to the student.
    student_status_groups = Record.is_recorded_in_groups(student, group_ids)
    student_can_enqueue = Record.can_enqueue_groups(student, course.groups.all())
    student_can_dequeue = Record.can_dequeue_groups(student, course.groups.all())

    for group in groups:
        group.num_enrolled = groups_stats.get(group.pk).get('num_enrolled')
        group.num_enqueued = groups_stats.get(group.pk).get('num_enqueued')
        group.is_enrolled = student_status_groups.get(group.pk).get('enrolled')
        group.is_enqueued = student_status_groups.get(group.pk).get('enqueued')
        group.can_enqueue = student_can_enqueue.get(group.pk)
        group.can_dequeue = student_can_dequeue.get(group.pk)

    teachers = {g.teacher for g in groups}

    data = {
        'course': course,
        'teachers': teachers,
        'points': course.get_points(student),
        'groups': groups,
    }

    if request.is_ajax():
        rendered_html = render_to_string('courses/course_info.html', data, request)
        return JsonResponse({
            'courseHtml': rendered_html,
            'courseName': course.name,
            'courseEditLink': reverse('admin:courses_course_change', args=[course.pk])
        })
    data.update(prepare_courses_list_to_render(request, course.semester))
    return render(request, 'courses/course.html', data)


@login_required
def group_view(request, group_id):
    """Group records view - list of all students enrolled and enqueued to group.
    """
    group: Group = None
    try:
        group = Group.objects.select_related('course', 'course__semester').prefetch_related(
            'term', 'term__classroom'
        ).get(id=group_id)
    except Group.DoesNotExist:
        raise Http404

    records = Record.objects.filter(group_id=group_id).exclude(
        status=RecordStatus.REMOVED
    ).select_related('student', 'student__user', 'student__program', 'student__consent')
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
        'mailto_group': mailto(request.user, students_in_group, bcc=False),
        'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
        'mailto_group_bcc': mailto(request.user, students_in_group, bcc=True),
        'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    })
    return render(request, 'courses/group.html', data)


def recorded_students_csv(group_id: int, status: RecordStatus) -> HttpResponse:
    """Builds the HttpResponse with list of student enrolled/enqueued in group.
    """
    students_in_group = Record.objects.filter(
        group_id=group_id, status=status
    ).select_related('student', 'student__user')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="group-{}-{}.csv"'.format(
        group_id, status.label
    )

    writer = csv.writer(response)
    for student in students_in_group:
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

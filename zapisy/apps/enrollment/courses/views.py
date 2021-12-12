import csv
import json
from typing import Dict, Iterable, List, Optional, Tuple

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group, GuaranteedSpots
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record, RecordStatus
from apps.enrollment.utils import mailto
from apps.users.decorators import employee_required
from apps.users.models import Student, is_external_contractor


def prepare_courses_list_data(semester: Optional[Semester]):
    """Returns a dict used by course list and filter in various views."""
    qs = CourseInstance.objects.filter(semester=semester).order_by('name')
    courses = []
    for course in qs.prefetch_related('effects', 'tags'):
        course_dict = course.__json__()
        course_dict.update({
                'url': reverse('course-page', args=(course.slug,)),
            })
        courses.append(course_dict)
    filters_dict = CourseInstance.prepare_filter_data(qs)
    all_semesters = Semester.objects.filter(visible=True)
    return {
        'semester': semester,
        'all_semesters': all_semesters,
        'courses_json': json.dumps(courses),
        'filters_json': json.dumps(filters_dict),
    }


def courses_list(request, semester_id: Optional[int] = None):
    """A basic courses view with courses listed on the right and no course selected."""
    semester: Optional[Semester]
    if semester_id is None:
        semester = Semester.get_upcoming_semester()
    else:
        semester = get_object_or_404(Semester, pk=semester_id)
    data = prepare_courses_list_data(semester)
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
        'teacher',
        'teacher__user',
    ).prefetch_related('term', 'term__classrooms', 'guaranteed_spots', 'guaranteed_spots__role')

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
    data.update(prepare_courses_list_data(course.semester))
    return render(request, 'courses/courses.html', data)


@login_required
def course_list_view(request, slug):
    course: CourseInstance
    try:
        course = (
            CourseInstance.objects.filter(slug=slug)
            .select_related('semester', 'course_type')
            .prefetch_related('tags', 'effects')
            .get()
        )
    except CourseInstance.DoesNotExist:
        return None, None


    def get_group_data(group_id):
        group: Group
        try:
            group = (
                Group.objects.select_related(
                    'course', 'course__semester', 'teacher', 'teacher__user'
                )
                .prefetch_related('term', 'term__classrooms')
                .get(id=group_id)
            )
        except Group.DoesNotExist:
            raise Http404

        records_in_group = (
            Record.objects.filter(group_id=group_id, status=RecordStatus.ENROLLED)
            .select_related(
                'student', 'student__user', 'student__program', 'student__consent'
            )
            .prefetch_related('student__user__groups')
            .order_by('student__user__last_name', 'student__user__first_name')
        )
        records_in_queue = (
            Record.objects.filter(group_id=group_id, status=RecordStatus.QUEUED)
            .select_related(
                'student', 'student__user', 'student__program', 'student__consent'
            )
            .prefetch_related('student__user__groups')
            .order_by('created')
        )


        def collect_students(records) -> List[Student]:
            return [record.student for record in records]


        students_in_group = collect_students(records_in_group)
        students_in_queue = collect_students(records_in_queue)

        data = {
            f'students_in_group': students_in_group,
            f'students_in_queue': students_in_queue,
            f'group': group,
            f'can_user_see_all_students_here': can_user_view_students_list_for_group(
                request.user, group
            ),
        }

        return data


    def sort_student_by_name(students: List[Student]) -> List[Student]:
        return sorted(students, key=lambda e: (e.user.last_name, e.user.first_name))


    groups_ids = [group.id for group in course.groups.all()]
    groups_data = [get_group_data(id) for id in groups_ids]
    can_user_see_all_students_here = all(
                [group['can_user_see_all_students_here'] for group in groups_data]
            )
    students_in_course = set()
    students_in_queue = set()

    for group_data in groups_data:
        students_in_course.update(group_data['students_in_group'])
    for group_data in groups_data:
        students_in_queue.update([student for student in group_data['students_in_queue'] if student not in students_in_course])
        
    data = {
            'students_in_course': sort_student_by_name(students_in_course),
            'students_in_queue': sort_student_by_name(students_in_queue),
            'course': course,
            'can_user_see_all_students_here': can_user_see_all_students_here,
            'mailto_group': mailto(request.user, students_in_course, bcc=False),
            'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
            'mailto_group_bcc': mailto(request.user, students_in_course, bcc=True),
            'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    }
    return render(request, 'courses/course_parts/course_list.html', data)


def can_user_view_students_list_for_group(user: User, group: Group) -> bool:
    """Is user authorized to see students' names in the given group?"""
    is_user_proper_employee = (user.employee and not is_external_contractor(user))
    is_user_group_teacher = user == group.teacher.user
    return is_user_proper_employee or is_user_group_teacher


@login_required
def group_view(request, group_id):
    """Group records view.

    Presents list of all students enrolled and enqueued to group.
    """
    group: Group
    try:
        group = Group.objects.select_related(
                'course', 'course__semester', 'teacher', 'teacher__user'
            ).prefetch_related('term', 'term__classrooms').get(id=group_id)
    except Group.DoesNotExist:
        raise Http404

    records_in_group = Record.objects.filter(
        group_id=group_id, status=RecordStatus.ENROLLED).select_related(
            'student', 'student__user', 'student__program',
            'student__consent').prefetch_related('student__user__groups').order_by(
                'student__user__last_name', 'student__user__first_name')

    records_in_queue = Record.objects.filter(
        group_id=group_id, status=RecordStatus.QUEUED).select_related(
            'student', 'student__user', 'student__program',
            'student__consent').prefetch_related('student__user__groups').order_by('created')

    guaranteed_spots_rules = GuaranteedSpots.objects.filter(group=group)

    def collect_students(records) -> List[Student]:
        record: Record
        student_list = []
        for record in records:
            record.student.guaranteed = set(rule.role.name for rule in guaranteed_spots_rules) & set(
                role.name for role in record.student.user.groups.all())
            student_list.append(record.student)
        return student_list

    students_in_group = collect_students(records_in_group)
    students_in_queue = collect_students(records_in_queue)

    data = {
        'students_in_group': students_in_group,
        'students_in_queue': students_in_queue,
        'guaranteed_spots': guaranteed_spots_rules,
        'group': group,
        'can_user_see_all_students_here': can_user_view_students_list_for_group(
            request.user, group),
        'mailto_group': mailto(request.user, students_in_group, bcc=False),
        'mailto_queue': mailto(request.user, students_in_queue, bcc=False),
        'mailto_group_bcc': mailto(request.user, students_in_group, bcc=True),
        'mailto_queue_bcc': mailto(request.user, students_in_queue, bcc=True),
    }
    data.update(prepare_courses_list_data(group.course.semester))
    return render(request, 'courses/group.html', data)


def recorded_students_csv(
    group_ids: List[int],
    status: RecordStatus,
    course_name: Optional[str] = None,
    exclude_matriculas: Optional[Iterable] = None
) -> HttpResponse:
    """Builds the HttpResponse with list of student enrolled/enqueued in a list of groups."""
    exclude_matriculas = exclude_matriculas or ()
    order = 'student__user__last_name' if status == RecordStatus.ENROLLED else 'created'
    students = {}
    for group_id in group_ids:
        records_in_group = Record.objects.filter(
            group_id=group_id, status=status
            ).select_related('student', 'student__user').order_by(order)
        for record in records_in_group:
            if record.student.matricula not in exclude_matriculas:
                students[record.student.matricula] = {
                    "first_name": record.student.user.first_name,
                    "last_name": record.student.user.last_name,
                    "email": record.student.user.email,
                }

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.csv"'.format(
        "course" if course_name else "group", course_name if course_name else group_ids[0], status.label
    )

    writer = csv.writer(response)
    for matricula, student in students.items():
            writer.writerow([
                    student["first_name"], student["last_name"], matricula, student["email"]
                ])
    return response


@employee_required
def group_enrolled_csv(request, group_id):
    """Prints out the group members in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return recorded_students_csv([group_id], RecordStatus.ENROLLED)


@employee_required
def group_queue_csv(request, group_id):
    """Prints out the group queue in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return recorded_students_csv([group_id], RecordStatus.QUEUED)


def get_all_group_ids_for_course_slug(slug):
    """Return a tuple course short_name and a list of groups ids."""
    course: CourseInstance
    try:
        course = (
            CourseInstance.objects.filter(slug=slug)
            .select_related('semester', 'course_type')
            .prefetch_related('tags', 'effects')
            .get()
        )
    except CourseInstance.DoesNotExist:
        return None, None

    name = course.short_name if course.short_name else course.name
    return (name, [group.id for group in course.groups.all()])


@employee_required
def course_enrolled_csv(request, course_slug):
    """Prints out the course members in csv format."""
    course_short_name, group_ids = get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    return recorded_students_csv(group_ids, RecordStatus.ENROLLED, course_short_name)


@employee_required
def course_queue_csv(request, course_slug):
    """Prints out the course queue in csv format."""
    course_short_name, group_ids = get_all_group_ids_for_course_slug(course_slug)

    students_enrolled = set()
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404

        records_in_group = (
            Record.objects.filter(group_id=group_id, status=RecordStatus.ENROLLED)
            .select_related(
                'student', 'student__user', 'student__program', 'student__consent'
            )
            .prefetch_related('student__user__groups')
            .order_by('student__user__last_name', 'student__user__first_name')
        )
        students_enrolled.update([record.student.matricula for record in records_in_group])

    return recorded_students_csv(group_ids, RecordStatus.QUEUED, course_short_name, exclude_matriculas=students_enrolled)

import csv
import json
import locale
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple, TypedDict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Min
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

locale.setlocale(locale.LC_ALL, "pl_PL.UTF-8")


class GroupData(TypedDict):
    students: List[Student]
    group: Group
    guaranteed_spots_rules: set
    can_user_see_all_students_here: bool


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
    enrolled = Record.taken_spots_by_role(groups)

    all_guaranteed_spots = GuaranteedSpots.objects.filter(group__in=groups)
    group_roles_limits = defaultdict(int)
    for gs in all_guaranteed_spots:
        group_roles_limits[gs.group.id] += gs.limit

    for group in groups:
        group.total_limit = group.limit + group_roles_limits[group.pk]
        group.total_enrolled = 0 #groups_stats.get(group.pk).get('num_enrolled')
        group.num_enrolled = enrolled[group.pk].pop("")
        group.role_enrolled = group.total_enrolled - group.num_enrolled
        group.num_enrolled_by_role = enrolled[group.pk]
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


def get_group_data(group_ids: List[int], user: User, status: RecordStatus) -> Dict[int, GroupData]:
    """Retrieves a group and relevant data for each group id of group_ids list.

    If the group does not exist skip it. If no group exists return an empty dictionary.
    """
    data = {}
    for group_id in group_ids:
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

        records = (
            Record.objects.filter(group_id=group_id, status=status)
            .select_related(
                'student', 'student__user', 'student__program', 'student__consent'
            )
            .prefetch_related('student__user__groups').order_by('created')
        )

        guaranteed_spots_rules = GuaranteedSpots.objects.filter(group=group)
        students: List[Student] = []
        for record in records:
            record.student.guaranteed = set(rule.role.name for rule in guaranteed_spots_rules) & set(
                role.name for role in record.student.user.groups.all())
            students.append(record.student)

        data[group_id] = {
            'students': students,
            'group': group,
            'guaranteed_spots_rules': guaranteed_spots_rules,
            'can_user_see_all_students_here': can_user_view_students_list_for_group(
                user, group
            ),
        }

    return data


def get_students_from_data(
    groups_data_enrolled: Dict[int, GroupData],
    groups_data_queued: Dict[int, GroupData],
    preserve_queue_ordering: bool = False,
):
    def sort_student_by_name(students: List[Student]) -> List[Student]:
        return sorted(students, key=lambda e: (locale.strxfrm(e.user.last_name),
                                               locale.strxfrm(e.user.first_name)))

    students_in_course = set()
    students_in_queue = []

    for group_data in groups_data_enrolled.values():
        students_in_course.update(group_data["students"])
    for group_data in groups_data_queued.values():
        students_in_queue.extend([
            student
            for student in group_data["students"]
            if student not in students_in_course
        ])

    students_in_course = sort_student_by_name(students_in_course)
    if not preserve_queue_ordering:
        students_in_queue = sort_student_by_name(set(students_in_queue))

    return students_in_course, students_in_queue


@login_required
def course_list_view(request, course_slug: str, class_type: int = None):
    course, _, groups_ids = get_all_group_ids_for_course_slug(course_slug, class_type=class_type)
    groups_data_enrolled = get_group_data(groups_ids, request.user, status=RecordStatus.ENROLLED)
    groups_data_queued = get_group_data(groups_ids, request.user, status=RecordStatus.QUEUED)

    students_in_course, students_in_queue = get_students_from_data(
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
    data.update(prepare_courses_list_data(course.semester))
    return render(request, 'courses/course_list.html', data)


def can_user_view_students_list_for_group(user: User, group: Group) -> bool:
    """Is user authorized to see students' names in the given group?"""
    is_user_proper_employee = (user.employee and not is_external_contractor(user))
    is_user_group_teacher = group.teacher is not None and user == group.teacher.user
    return is_user_proper_employee or is_user_group_teacher


@login_required
def group_view(request, group_id):
    """Group records view.

    Presents list of all students enrolled and enqueued to group.
    """
    enrolled_data = get_group_data([group_id], request.user, status=RecordStatus.ENROLLED)
    queued_data = get_group_data([group_id], request.user, status=RecordStatus.QUEUED)
    students_in_group, students_in_queue = get_students_from_data(
        enrolled_data, queued_data, preserve_queue_ordering=True
    )
    group: Group = enrolled_data[group_id].get("group")

    limits_for_roles = [gs.limit for gs in GuaranteedSpots.objects.filter(group=group)]
    group.total_limit = group.limit + sum(limits_for_roles)

    enrolled = Record.taken_spots_by_role([group])
    group.num_enrolled = enrolled[group.pk].pop("")
    group.num_enrolled_by_role = enrolled[group.pk]

    data = {
        'students_in_group': students_in_group,
        'students_in_queue': students_in_queue,
        'guaranteed_spots': enrolled_data.get('guaranteed_spots_rules'),
        'spots_by_role': [(gs, enrolled[group.pk][gs.role.name]) for gs in group.guaranteed_spots.all()],
        'group': group,
        'can_user_see_all_students_here': enrolled_data[group_id].get("can_user_see_all_students_here"),
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
    user: User,
    course_name: Optional[str] = None,
    exclude_students: Optional[Iterable] = None,
    *, preserve_ordering: bool = False,
) -> HttpResponse:
    """Builds the HttpResponse with list of student enrolled/enqueued in a list of groups."""
    exclude_students = set(exclude_students or [])
    students = []
    group_data = get_group_data(group_ids, user, status)
    for group in group_data.values():
        for student in group.get("students", []):
            if student not in exclude_students:
                exclude_students.add(student)
                students.append((student.matricula, {
                    "first_name": student.user.first_name,
                    "last_name": student.user.last_name,
                    "email": student.user.email,
                }))
    if not preserve_ordering:
        students.sort(key=lambda e: (locale.strxfrm(e[1].get("last_name")),
                                     locale.strxfrm(e[1].get("first_name"))))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.csv"'.format(
        "course" if course_name else "group", course_name if course_name else group_ids[0], status.label
    )

    writer = csv.writer(response)
    for matricula, student in students:
        writer.writerow([
                student["first_name"], student["last_name"], matricula, student["email"]
            ])
    return response


@employee_required
def group_enrolled_csv(request, group_id):
    """Prints out the group members in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return recorded_students_csv([group_id], RecordStatus.ENROLLED, request.user)


@employee_required
def group_queue_csv(request, group_id):
    """Prints out the group queue in csv format."""
    if not Group.objects.filter(id=group_id).exists():
        raise Http404
    return recorded_students_csv([group_id], RecordStatus.QUEUED, request.user, preserve_ordering=True)


def get_all_group_ids_for_course_slug(slug, class_type: int = None):
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
    return (course, name, [group.id for group in course.groups.all() if class_type is None or group.type == class_type])


@employee_required
def course_enrolled_csv(request, course_slug):
    """Prints out the course members in csv format."""
    _, course_short_name, group_ids = get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    return recorded_students_csv(group_ids, RecordStatus.ENROLLED, request.user, course_short_name)


@employee_required
def course_queue_csv(request, course_slug):
    """Prints out the course queue in csv format."""
    _, course_short_name, group_ids = get_all_group_ids_for_course_slug(course_slug)
    for group_id in group_ids:
        if not Group.objects.filter(id=group_id).exists():
            raise Http404
    group_data = get_group_data(group_ids, request.user, status=RecordStatus.ENROLLED)

    students_enrolled = set()
    for group in group_data.values():
        students_enrolled.update(group.get("students", []))

    return recorded_students_csv(
        group_ids,
        RecordStatus.QUEUED,
        request.user,
        course_short_name,
        exclude_students=students_enrolled
    )

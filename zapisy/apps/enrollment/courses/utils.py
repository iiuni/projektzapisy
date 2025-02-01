import csv
import json
import locale
from typing import Dict, Iterable, List, Optional, TypedDict

from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.group import Group, GuaranteedSpots
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record, RecordStatus
from apps.users.models import Student
from apps.enrollment.courses.permissions import can_user_view_students_list_for_group


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
        return None, None, []

    name = course.short_name if course.short_name else course.name
    return (course, name, [group.id for group in course.groups.all() if class_type is None or group.type == class_type])


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

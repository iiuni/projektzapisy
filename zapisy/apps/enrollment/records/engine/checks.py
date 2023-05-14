import copy
from typing import Iterable, List, Optional

from apps.enrollment.courses.models import CourseInstance, Group, Semester
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.users.models import Student


def is_enrolled(student: Student, group: Group) -> bool:
    """Checks if the student is already enrolled into the group."""
    records = Record.objects.filter(
        student=student, group=group, status=RecordStatus.ENROLLED)
    return records.exists()


def is_recorded(student: Student, group: Group) -> bool:
    """Checks if the student is already enrolled or enqueued into the group."""
    entry = is_recorded_in_groups(student, [group])[0]
    return getattr(entry, 'is_enqueued', False) or getattr(entry, 'is_enrolled', False)


def is_recorded_in_groups(student: Optional[Student],
                          groups: Iterable[Group]) -> List[Group]:
    """Checks, in which groups the student is already enrolled or enqueued.

    The function modifies provided groups by setting additional attributes:
    'is_enrolled', 'is_enqueued' and 'priority'. The attributes must always
    be checked with a default, because they are sometimes skipped.
    """
    groups = [copy.copy(g) for g in groups]
    if student is None:
        return groups
    records = Record.objects.filter(student=student,
                                    group_id__in=groups).exclude(status=RecordStatus.REMOVED)
    by_group = {record.group_id: record for record in records}
    for group in groups:
        if group.id not in by_group:
            continue
        record = by_group[group.id]
        if record.status in [RecordStatus.QUEUED, RecordStatus.BLOCKED]:
            setattr(group, 'is_enqueued', True)
            setattr(group, 'priority', record.priority)
        elif record.status == RecordStatus.ENROLLED:
            setattr(group, 'is_enrolled', True)
    return groups


def student_points_in_semester(student: Student, semester: Semester,
                               additional_courses: Iterable[CourseInstance] = []) -> int:
    """Returns total points the student has accumulated in semester.

    Args:
        additional_courses is a list of potential courses a student might
        also want to enroll into.
    """
    records = Record.objects.filter(
        student=student,
        group__course__semester=semester, status=RecordStatus.ENROLLED).select_related(
            'group', 'group__course')
    courses = set(r.group.course for r in records)
    courses.update(additional_courses)
    return sum(c.points for c in courses)

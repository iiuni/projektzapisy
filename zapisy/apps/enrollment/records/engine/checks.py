import copy
from collections import defaultdict
from typing import DefaultDict, Dict, Iterable, List, Optional, Set

from django.contrib.auth.models import User
from django.db import models

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


def list_waiting_students(
        courses: List[CourseInstance]) -> DefaultDict[int, DefaultDict[int, int]]:
    """Returns students waiting to be enrolled.

    Returned students aren't enrolled in any group of given type within
    given course, but they are enqueued into at least one.

    Returns:
        A dict indexed by a course_id. Every entry is a dict mapping
        group_type to a number of waiting students.
    """
    queued = Record.objects.filter(
        status__in=[RecordStatus.QUEUED, RecordStatus.BLOCKED], group__course__in=courses).values(
            'group__course', 'group__type', 'student__user',
            'student__user__first_name', 'student__user__last_name')
    enrolled = Record.objects.filter(
        status=RecordStatus.ENROLLED, group__course__in=courses).values(
            'group__course', 'group__type', 'student__user', 'student__user__first_name',
            'student__user__last_name')
    waiting = queued.difference(enrolled)
    ret = defaultdict(lambda: defaultdict(int))
    for w in waiting:
        ret[w['group__course']][w['group__type']] += 1
    return ret


def groups_stats(groups: List[Group]) -> Dict[int, Dict[str, int]]:
    """For a list of groups returns number of enqueued and enrolled students.

    The data will be returned in the form of a dict indexed by group id.
    Every entry will be a dict with fields 'num_enrolled' and
    'num_enqueued'.
    """
    enrolled_agg = models.Count('id', filter=models.Q(status=RecordStatus.ENROLLED))
    enqueued_agg = models.Count('id', filter=models.Q(status__in=[RecordStatus.QUEUED, RecordStatus.BLOCKED]))
    records = Record.objects.filter(group__in=groups).exclude(
        status=RecordStatus.REMOVED).values('group_id').annotate(
            num_enrolled=enrolled_agg, num_enqueued=enqueued_agg).values(
                'group_id', 'num_enrolled', 'num_enqueued')
    ret_dict: Dict[int, Dict[str, int]] = {
        g.pk: {
            'num_enrolled': 0,
            'num_enqueued': 0
        }
        for g in groups
    }
    for rec in records:
        ret_dict[rec['group_id']]['num_enrolled'] = rec['num_enrolled']
        ret_dict[rec['group_id']]['num_enqueued'] = rec['num_enqueued']
    return ret_dict


def common_groups(user: User, groups: List[Group]) -> Set[int]:
    """Returns ids of those of groups that user is involved in.

    User may be an employee — we then return groups he is teaching. If user
    is a student, we return those of the groups, he is enrolled into. If
    user is neither a student nor an employee, an empty set is returned.
    """
    common_groups = set()
    if user.student:
        student_records = Record.objects.filter(
            group__in=groups, student=user.student, status=RecordStatus.ENROLLED)
        common_groups = {r.group_id for r in student_records}
    if user.employee:
        common_groups = set(
            Group.objects.filter(pk__in=[g.pk for g in groups],
                                 teacher=user.employee).values_list('pk', flat=True))
    return common_groups

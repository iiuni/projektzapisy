import copy
from typing import Iterable, List, Optional

from apps.enrollment.courses.models import Group
from apps.enrollment.records.models.records import Record, RecordStatus
from apps.users.models import Student


def is_enrolled(student: Student, group: Group) -> bool:
    """Checks if the student is already enrolled into the group."""
    records = Record.objects.filter(
        student=student, group=group, status=RecordStatus.ENROLLED)
    return records.exists()


def is_recorded(student: Student, group: Group) -> bool:
    """Checks if the student is already enrolled or enqueued into the group."""
    entry = Record.is_recorded_in_groups(student, [group])[0]
    return getattr(entry, 'is_enqueued', False) or getattr(entry, 'is_enrolled', False)



from apps.enrollment.courses.models import Group
from apps.enrollment.records.models.records import Record, RecordStatus


def update_records_in_auto_enrollment_group(group_id: int):
    """Automatically syncs students in an auto-enrollment group.

    Auto-enrollment groups must always reflect the state of other groups in
    the course: people enrolled to some other group must also be enrolled in
    the auto-enrollment group. People enqueued in other groups (but not
    enrolled in any) will be enqueued in the auto-enrollment group. Everyone
    else must be out.

    Args:
        group_id: Must be an id of a auto-enrollment group.
    """
    other_groups = Group.objects.filter(course__groups=group_id, auto_enrollment=False)

    def get_all_students(**kwargs):
        qs = Record.objects.filter(**kwargs)
        return set(qs.values_list('student_id', flat=True).distinct())

    enrolled_other = get_all_students(group__in=other_groups, status=RecordStatus.ENROLLED)
    queued_other = get_all_students(group__in=other_groups, status=RecordStatus.QUEUED)
    enrolled_in_group = get_all_students(group=group_id, status=RecordStatus.ENROLLED)
    queued_in_group = get_all_students(group=group_id, status=RecordStatus.QUEUED)
    # First we enqueue people who are in some groups but are completely absent in our group.
    missing_students = (enrolled_other | queued_other) - (enrolled_in_group | queued_in_group)
    Record.objects.bulk_create([
        Record(student_id=s, group_id=group_id, status=RecordStatus.QUEUED)
        for s in missing_students
    ])
    # We change the status from queued to enrolled for those, who should be enrolled.
    Record.objects.filter(group=group_id, status=RecordStatus.QUEUED,
                          student_id__in=enrolled_other).update(status=RecordStatus.ENROLLED)
    # We change the status from enrolled to queued for those who should be queued.
    Record.objects.filter(
        group=group_id,
        status=RecordStatus.ENROLLED,
        student_id__in=(queued_other - enrolled_other)).update(status=RecordStatus.QUEUED)
    # Drop records of people not in the group.
    Record.objects.filter(group_id=group_id).exclude(status=RecordStatus.REMOVED).exclude(
        student_id__in=(enrolled_other | queued_other)).update(status=RecordStatus.REMOVED)

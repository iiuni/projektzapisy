"""Business logic for director's discharge requests.

Public API:
    can_request_discharge(student, course, time=None) -> (bool, str)
    get_discharges_used_total(student) -> int
    get_discharges_used_in_semester(student, semester) -> int
    request_discharge(student, course) -> DirectorDischarge
    approve_discharge(discharge, admin_user) -> None
    reject_discharge(discharge, admin_user, comment='') -> None
"""

import logging
from datetime import datetime

from apps.enrollment.records.models.records import Record, RecordStatus
from apps.enrollment.records.signals import GROUP_CHANGE_SIGNAL

from .models import DirectorDischarge, DischargeStatus

LOGGER = logging.getLogger(__name__)


def get_discharges_used_total(student):
    """Returns the number of approved director discharges the student has used."""
    return DirectorDischarge.objects.filter(
        student=student, status=DischargeStatus.APPROVED
    ).count()


def get_discharges_used_in_semester(student, semester):
    """Returns the number of approved director discharges in a given semester."""
    return DirectorDischarge.objects.filter(
        student=student,
        status=DischargeStatus.APPROVED,
        course__semester=semester,
    ).count()


def can_request_discharge(student, course, time=None):
    """Checks whether the student can submit a director discharge request.

    Returns:
        (True, '') if the request is allowed.
        (False, reason) if not, where reason is a human-readable message.

    Conditions (all must be met):
        - student is active
        - student is enrolled (ENROLLED status) in at least one group of the course
        - current time is after semester's records_closing
        - current time is before semester's director_discharge_deadline (if set)
        - no existing PENDING or APPROVED discharge for this (student, course) pair
        - student hasn't exceeded their total discharge_limit
        - student hasn't already used a discharge in this semester (max 1 per semester)
    """
    if time is None:
        time = datetime.now()

    if student is None or not student.is_active:
        return False, 'Konto studenta jest nieaktywne.'

    semester = course.semester

    # Must be after records_closing
    if semester.records_closing is None or time <= semester.records_closing:
        return False, 'Składanie wniosków jest możliwe dopiero po zamknięciu zapisów.'

    # Must be before director_discharge_deadline (if set)
    if semester.director_discharge_deadline is not None:
        if time > semester.director_discharge_deadline:
            return False, 'Termin składania wniosków o wypis dyrektorski minął.'

    # Student must be enrolled in at least one group of the course
    enrolled = Record.objects.filter(
        student=student,
        group__course=course,
        status=RecordStatus.ENROLLED,
    ).exists()
    if not enrolled:
        return False, 'Nie jesteś zapisany na żadną grupę tego przedmiotu.'

    # No duplicate pending/approved request
    existing = DirectorDischarge.objects.filter(
        student=student,
        course=course,
        status__in=[DischargeStatus.PENDING, DischargeStatus.APPROVED],
    ).exists()
    if existing:
        return False, 'Wniosek o wypis dyrektorski dla tego przedmiotu już istnieje.'

    # Total limit check
    used_total = get_discharges_used_total(student)
    if used_total >= student.discharge_limit:
        return False, (
            f'Wyczerpano limit wypisów dyrektorskich '
            f'({used_total}/{student.discharge_limit}).'
        )

    # Max 1 per semester — block if there's already a pending or approved request in this semester
    existing_in_semester = DirectorDischarge.objects.filter(
        student=student,
        course__semester=semester,
        status__in=[DischargeStatus.PENDING, DischargeStatus.APPROVED],
    ).exists()
    if existing_in_semester:
        return False, 'Możliwy jest tylko jeden wypis dyrektorski w semestrze.'

    return True, ''


def request_discharge(student, course):
    """Creates a pending director discharge request.

    Raises:
        ValueError: If the student is not eligible (can_request_discharge fails).
    """
    allowed, msg = can_request_discharge(student, course)
    if not allowed:
        raise ValueError(msg)

    discharge = DirectorDischarge.objects.create(
        student=student,
        course=course,
        status=DischargeStatus.PENDING,
    )
    LOGGER.info('Director discharge request created: student=%s course=%s', student, course)
    return discharge


def approve_discharge(discharge, admin_user):
    """Approves a director discharge request.

    Removes the student from all enrolled/queued groups of the course,
    bypassing the normal deadline restrictions (this is an admin override).

    Raises:
        ValueError: If the discharge is not in PENDING status.
    """
    if discharge.status != DischargeStatus.PENDING:
        raise ValueError(
            f'Wniosek nie jest w stanie oczekującym (aktualny status: '
            f'{discharge.get_status_display()}).'
        )

    student = discharge.student
    course = discharge.course

    # Remove student from all non-removed records in this course (admin bypass)
    records = Record.objects.filter(
        student=student,
        group__course=course,
    ).exclude(status=RecordStatus.REMOVED)

    # Collect group IDs before deleting records (after update the queryset changes)
    affected_group_ids = []
    for record in records:
        affected_group_ids.append(record.group_id)

    # Directly set to REMOVED (bypasses can_dequeue deadline check)
    records.update(status=RecordStatus.REMOVED)

    # Trigger queue-fill for each vacated group
    for group_id in affected_group_ids:
        GROUP_CHANGE_SIGNAL.send(None, group_id=group_id)

    discharge.status = DischargeStatus.APPROVED
    discharge.decided_by = admin_user
    discharge.decided_at = datetime.now()
    discharge.save()

    LOGGER.info(
        'Director discharge approved: student=%s course=%s by=%s',
        student, course, admin_user,
    )


def reject_discharge(discharge, admin_user, comment=''):
    """Rejects a director discharge request.

    The student remains enrolled in their groups.

    Raises:
        ValueError: If the discharge is not in PENDING status.
    """
    if discharge.status != DischargeStatus.PENDING:
        raise ValueError(
            f'Wniosek nie jest w stanie oczekującym (aktualny status: '
            f'{discharge.get_status_display()}).'
        )

    discharge.status = DischargeStatus.REJECTED
    discharge.decided_by = admin_user
    discharge.decided_at = datetime.now()
    discharge.admin_comment = comment
    discharge.save()

    LOGGER.info(
        'Director discharge rejected: student=%s course=%s by=%s',
        discharge.student, discharge.course, admin_user,
    )

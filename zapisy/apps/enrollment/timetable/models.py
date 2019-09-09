"""Models for the timetable prototype."""
from typing import Iterable

from django.contrib.auth.models import Group as AuthGroup
from django.db import models

from apps.enrollment.courses.models import Group, Semester
from apps.users.models import Student


class Pin(models.Model):
    """Pin keeps the course group on a student's timetable prototype.

    The prototype will always show the student the courses, he is enrolled or
    enqueued into. Sometimes students wish to _pin_ a course to the timetable
    prototype — typically, when they cannot enqueue yet but try to collect the
    dream course groups for their semester.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "group")
        indexes = [
            models.Index(fields=["student", "group"])
        ]

    @classmethod
    def student_pins_in_semester(cls, student: Student, semester: Semester) -> Iterable[Group]:
        """Returns the groups that student has pinned in the semester."""
        pins = cls.objects.filter(
            group__course__semester_id=semester.pk, student_id=student.pk).select_related(
                'group__course', 'group__teacher', 'group__teacher__user')
        return map(lambda p: p.group, pins)


class HiddenGroups(models.Model):
    """HiddenGroups is a way to hide groups from students in the prototype.

    Sometimes we will have parallel virtual course groups. A student will only
    be allowed to enrol into one of them, the other will be closed. This allows
    us to hide these groups from him in the prototype for convenience. We don't
    hide groups from students individually, but rather we collect students in
    auth.Group.

    The prototype will override the HiddenGroups record and show the group to
    the student if he can enqueue to the group (determined by
    `apps.enrollment.records.models.Records.can_enqueue` function) or is already
    recorded in it.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.ForeignKey(AuthGroup, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("group", "role")
        indexes = [
            models.Index(fields=["group", "role"]),
        ]

    @classmethod
    def hidden_groups_for_student(cls, student: Student, groups: Iterable[Group]) -> Iterable[int]:
        """Returns the ids of groups hidden for a student within a collection.
        """
        roles = student.user.groups.all()
        hidden_groups = cls.objects.filter(
            role__in=roles, group__in=groups).values_list(
                'group_id', flat=True)
        return hidden_groups

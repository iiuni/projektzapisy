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

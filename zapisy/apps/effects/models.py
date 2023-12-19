from typing import Set

from django.db import models

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.users.models import Program, Student


# Model for completed courses
class CompletedCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course', 'program')

    def get_completed_effects(student: Student) -> Set[str]:
        completed_courses = (
            CompletedCourses.objects.filter(student=student, program=student.program)
            .select_related('course').prefetch_related('course__effects')
        )

        done_effects = set()
        for record in completed_courses:
            for effect in record.course.effects.all():
                done_effects.add(effect.group_name)

        return done_effects

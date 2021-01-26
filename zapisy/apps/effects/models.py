from typing import Set

from django.db import models

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.users.models import Student


# Model for completed courses
class CompletedCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')

    def get_completed_effects(student: Student) -> Set[str]:
        completed_courses = CompletedCourses.objects.filter(student=student)

        done_effects = set()
        for record in completed_courses:
            course_instance = CourseInstance.objects.get(id=record.course.id)
            for effect in course_instance.effects.all():
                done_effects.add(effect.group_name)

        return done_effects

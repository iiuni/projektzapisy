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

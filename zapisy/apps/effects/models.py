from django.db import models

from apps.users.models import Student
from apps.enrollment.courses.models.course_instance import CourseInstance
# from apps.enrollment.courses.models.effects import Effects


# Model for completed courses
class CompletedCourses(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    courses = models.ManyToManyField(CourseInstance, blank=True)


# # Model for completed effects
# class CompletedEffects(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     effects = models.ManyToManyField(Effects, blank=True, null=True)
#     # program = ?

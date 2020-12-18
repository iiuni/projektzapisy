from django.db import models

from apps.users.models import Student
from apps.enrollment.courses.models import CourseInstance, Effects


# Model for completed courses
class CompletedCourses(models.Model):
    # id?
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    courses = models.ManyToManyField(CourseInstance, blank=True, null=True)
    # program = ?   Czy to jest potrzebne? Program studiów jest również w modelu studenta.


# Model for completed effects
class CompletedEffects(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    effects = models.ManyToManyField(Effects, blank=True, null=True)
    # program = ?

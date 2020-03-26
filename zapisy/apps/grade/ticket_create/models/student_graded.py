from django.db import models
from apps.users.models import Student
from apps.enrollment.courses.models.semester import Semester


class StudentGraded(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="student")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name="semestr")

    class Meta:
        verbose_name = "udział w ocenie"
        verbose_name_plural = "udział w ocenie"
        unique_together = [['student', 'semester']]
        app_label = 'ticket_create'

    def __str__(self):
        return f"{self.student} wygenerował bilety oceny w semestrze {self.semester}"

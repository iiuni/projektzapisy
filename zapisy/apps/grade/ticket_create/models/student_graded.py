from django.db                import models
from apps.users.models      import Student
from apps.enrollment.courses.models import Semester

class StudentGraded( models.Model ):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name = "student")
    semester    = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name = "semestr")
    class Meta:
        verbose_name        = 'udzial w ocenie'
        verbose_name_plural = 'udzial w ocenie'
        app_label           = 'ticket_create'

    def __str__(self):
        return str( self.student ) + " " + str( self.semester )


from django.db import models
from django.db.models import Sum
from apps.users.models import Student

class PointTypes(models.Model):
    """types of points"""
    name = models.CharField(max_length=30, verbose_name='rodzaj punktów', default="", unique=False)

    class Meta:
        verbose_name = 'rodzaj punktu'
        verbose_name_plural = 'rodzaje punktów'
        app_label = 'courses'

    def __str__(self):
        return '%s' % (self.name, )

class PointsOfCourseEntities(models.Model):
    """
        Model przechowuje punkty przypisane do :model:`courses.CourseEntity` oraz :model:'courses.PointTypes'

        Pole program jest opcjonalne.

         * Zasada wyznaczenia punktów *

         Student X jest na programie Y. Sprawdzamy ile jest dla niego przedmiot Z.
         Jeżeli istnieje rekord łączący program z podstawą dostajemy wartość z niego.
         W przeciwnym wypadku zwracamy wartość z rekordu w którym program == Null, entity==Z, a typ punktów
         zgadza się z typem przypisanym do osoby.
         Jeżeli nie istnieje rekord spełniający powyższe przypadki zwracamy zero.

         * Uwaga *

         Przedmioty posiadające wersje L i M mają modyfikatory zmieniające program.

         Czytanie z tej tabeli powinno odbywać się poprzez metody z :model:`courses.CourseEntity`
         w innym wypadku ryzykujemy otrzymanie nieprawidłowej wartości.


    """
    entity = models.ForeignKey('CourseEntity', verbose_name='podstawa przedmiotu', on_delete=models.CASCADE)
    type_of_point = models.ForeignKey('PointTypes', verbose_name='rodzaj punktów', on_delete=models.CASCADE)
    program = models.ForeignKey('users.Program', verbose_name='Program Studiów', null=True, blank=True, default=None, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(verbose_name='liczba punktów', default=6)

    class Meta:
        verbose_name = 'zależność podstawa przedmiotu-punkty'
        verbose_name_plural = 'zależności podstawy przedmiotu-punkty'
        app_label = 'courses'
        unique_together = ('entity', 'type_of_point', 'program')

    def __str__(self):
        return '%s: %s %s' % (self.entity.name, self.value, self.type_of_point)


class StudentPointsView(models.Model):
    value   = models.SmallIntegerField()
    student = models.OneToOneField(Student, primary_key=True, on_delete=models.CASCADE)
    entity  = models.ForeignKey('courses.CourseEntity', on_delete=models.CASCADE)

    # just for testing
    #def save(self, **kwargs):
    #    raise NotImplementedError()

    class Meta:
        managed = False
        app_label = 'courses'


    @classmethod
    def get_student_points_in_semester(cls, student, semester):
        """

        Return sum of points in certain semester

        @param student: users.Student object
        @param semester: coruses.Semester object
        @return: Integer
        """
        from apps.enrollment.records.models import Record

        records = Record.enrolled.filter(student=student, group__course__semester=semester).values_list('group__course__entity_id', flat=True).distinct()

        return cls.get_points_for_entities(student, records)

    @classmethod
    def get_points_for_entities(cls, student, entities):
        """

        Return sum of student points for records

        @param student:
        @param records: Entity Id's list
        @return:
        """
        points = cls.objects.\
                 filter(student=student, entity__in=entities).\
                 aggregate(Sum('value'))
        # If there's no active term, value__sum will be None
        return points['value__sum'] or 0

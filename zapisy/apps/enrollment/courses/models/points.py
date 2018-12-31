"""Module points deals with values of the courses.

It would seem, that just having a field `credits` in CourseEntity model would do
the trick. Unfortunately, some courses have different value for different
students, depending on the program they are pursuing (BSc, MSc) and their
previous achievements.
"""

from typing import List, Optional, Dict

from django.db import models

from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.semester import Semester
from apps.users.models import Student


class PointTypes(models.Model):
    """types of points"""
    name = models.CharField(max_length=30, verbose_name='rodzaj punktów', default="", unique=False)

    class Meta:
        verbose_name = 'rodzaj punktu'
        verbose_name_plural = 'rodzaje punktów'
        app_label = 'courses'

    def __str__(self):
        return self.name


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
    entity = models.ForeignKey(
        'CourseEntity',
        verbose_name='podstawa przedmiotu',
        on_delete=models.CASCADE)
    type_of_point = models.ForeignKey(
        'PointTypes',
        verbose_name='rodzaj punktów',
        on_delete=models.CASCADE)
    program = models.ForeignKey(
        'users.Program',
        verbose_name='Program Studiów',
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(verbose_name='liczba punktów', default=6)

    class Meta:
        verbose_name = 'zależność podstawa przedmiotu-punkty'
        verbose_name_plural = 'zależności podstawy przedmiotu-punkty'
        app_label = 'courses'
        unique_together = ('entity', 'type_of_point', 'program')

    def __str__(self):
        return '%s: %s %s' % (self.entity.name, self.value, self.type_of_point)


class StudentPointsView:
    """Provides functions for counting ECTS points for a particular student.

    A course does not necessarily always carry the same number of ECTS points.
    It may earn differently depending on student's programme and the courses he
    has already passed. The functions here implement this logic.
    """

    @classmethod
    def student_points_in_semester(cls, student: Student, semester: Semester) -> int:
        """Computes sum of points in a semester from student's perspective.

        This function may give wrong historic result for a student who has
        passed a certain course (like 'dyskretna_l') in the meantime.
        """
        from apps.enrollment.records.models import Record, RecordStatus
        records = Record.objects.filter(
            student=student, group__course__semester=semester,
            status=RecordStatus.ENROLLED).values_list(
                'group__course__entity_id', flat=True).distinct()

        return cls.points_for_entities_total(student, records)

    @classmethod
    def student_points_in_semester_with_added_courses(cls, student: Student, semester: Semester,
                                                      additional_courses: List[Course]) -> int:
        """Computes sum of points in a semester from student's perspective.

        Apart from the courses, the student is already enrolled into, it counts
        in additional courses, in which he may not be present.

        This function may give wrong historic result for a student who has
        passed a certain course (like 'dyskretna_l') in the meantime.
        """
        from apps.enrollment.records.models import Record, RecordStatus
        records = Record.objects.filter(
            student=student, group__course__semester=semester,
            status=RecordStatus.ENROLLED).values_list(
                'group__course__entity_id', flat=True).distinct()
        all_courses = list(set(list(records) + [c.entity_id for c in additional_courses]))
        return cls.points_for_entities_total(student, all_courses)

    @classmethod
    def course_value_for_student(cls, student: Optional[Student], entity_id: int) -> int:
        """Computes the value (number of ECTS credits) of a given course for a
        student.
        """
        return cls.points_for_entities_total(student, [entity_id])

    @classmethod
    def points_for_entities_total(cls, student: Optional[Student], entity_ids: List[int]) -> int:
        """Computes sum of points of entities from a student's perspective.

        This function may give wrong historic result for a student who has
        passed a certain course (like 'dyskretna_l') in the meantime.
        """
        return sum(cls.points_for_entities(student, entity_ids).values())

    @classmethod
    def points_for_entities(cls, student: Optional[Student], entity_ids: List[int]) -> Dict[int, int]:
        """Computes points of entities from a student's perspective.

        This function may give wrong historic result for a student who has
        passed a certain course (like 'dyskretna_l') in the meantime.

        The computation will be performed by obtaining all
        PointsOfCourseEntities records for these courses and choosing the right
        one for each course separately. For every entity in the list we see, if
        it is one of the few special cases (compulsory courses with two levels).
        If not, the PointsOfCourseEntities object should match the users program
        or be None. The implementation looks crude, but it only performs a
        constant number of database queries.

        If the student is None, the function will return the default number of
        credits for the course.

        The returned Dict will be keyed by CourseEntity identifier.
        """

        def value_with_program(program_id, points_of_courseentities_list):
            """For a given program_id will find either the number of points
            associated with this program_id, or with None, if one does not
            exist.
            """
            poc: PointsOfCourseEntities
            if program_id is not None:
                for poc in points_of_courseentities_list:
                    if poc.program_id == program_id:
                        return poc.value
            # The program_id is not on the list.
            for poc in points_of_courseentities_list:
                if poc.program_id is None:
                    return poc.value
            return 0

        sum_points = 0
        entities = CourseEntity.objects.filter(
            pk__in=entity_ids).prefetch_related('pointsofcourseentities_set')
        points_per_entity: Dict[int, int] = dict()
        entity: CourseEntity
        for entity in entities:
            if student is None:
                sum_points += value_with_program(None, entity.pointsofcourseentities_set.all())
                continue
            program_id = student.program_id
            if entity.numeryczna_l and student.numeryczna_l:
                program_id = 1
            elif entity.dyskretna_l and student.dyskretna_l:
                program_id = 1
            elif entity.algorytmy_l and student.algorytmy_l:
                program_id = 1
            elif entity.programowanie_l and student.programowanie_l:
                program_id = 1
            points_per_entity[entity.id] = value_with_program(program_id, entity.pointsofcourseentities_set.all())
        return points_per_entity

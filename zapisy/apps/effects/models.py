from typing import Iterable, Set, Tuple

from django.db import models

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.models.tag import Tag as CourseTag
from apps.users.models import Program, Student


class CompletedCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course', 'program')

    @staticmethod
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

    @staticmethod
    def get_count_and_ects_by_types_and_tags(
        student: Student,
        course_types: Iterable[CourseType] = None,
        course_tags: Iterable[CourseTag] = None
    ) -> Tuple[int, int]:
        """Returns count and sum of ects of completed courses that meet given requirements.

        Courses must be completed by given student,
        be of given type and have at least one of given tags.

        If course_types is None, then courses of any type are matched.
        If course_tags is None, then courses with any tags are matched.
        """
        if course_types is None:
            course_types = CourseType.objects.all()
        if course_tags is None:
            course_tags = CourseTag.objects.all()

        # TODO: Add filtering by course tags
        completed_courses = CompletedCourses.objects.filter(
            student=student,
            program=student.program,
            course__course_type__in=course_types,
        )

        count = len(completed_courses)
        ects = sum([record.course.points for record in completed_courses])

        return count, ects


class Variant(models.Model):
    name = models.CharField(max_length=300, verbose_name='Nazwa')
    requirements = models.JSONField(verbose_name='Wymagania', blank=True)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, verbose_name='Program studiów'
    )

    class Meta:
        verbose_name: str = 'Wariant'
        verbose_name_plural: str = 'Warianty'
        unique_together = ('name', 'program')

    def __str__(self):
        return self.name

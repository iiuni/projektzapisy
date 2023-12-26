import logging
from typing import Union, Iterable

from django.shortcuts import render

from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.models.tag import Tag as CourseTag
from apps.effects.models import CompletedCourses, Variant
from apps.users.decorators import student_required
from apps.enrollment.courses.models import Semester

from .models import Student

logger = logging.getLogger()


def update_course_types(requirement: dict, summary: dict) -> Iterable[CourseType]:
    if 'typy_przedmiotow' not in requirement:
        return CourseType.objects.all()

    summary.update({'types': requirement.get('typy_przedmiotow')})
    return CourseType.objects.filter(short_name__in=requirement.get('typy_przedmiotow'))


def update_course_tags(requirement: dict, summary: dict) -> Iterable[CourseTag]:
    if 'tagi_przedmiotow' not in requirement:
        return CourseTag.objects.all()

    summary.update({'tags': requirement.get('tagi_przedmiotow')})
    return CourseTag.objects.filter(short_name__in=requirement.get('tagi_przedmiotow'))


def update_course_languages(requirement: dict, summary: dict) -> "list[str]":
    if 'jezyk_wykladowy' not in requirement:
        return ['pl', 'en']

    summary.update({'language': requirement.get('jezyk_wykladowy')})
    return [requirement.get('jezyk_wykladowy')]


def update_additional_info(requirement: dict, summary: dict) -> Union[str, None]:
    summary.update({'additional_info': requirement.get('dodatkowe_info')})
    return requirement.get('dodatkowe_info')


def update_courses(requirement: dict, courses: int, summary: dict) -> int:
    courses_needed = max(requirement.get('liczba_przedmiotow') - courses, 0)
    summary.update({'courses': courses_needed})
    if courses_needed > 0:
        summary.update({'fulfilled': False})
    if requirement.get('liczba_przedmiotow') == 1:
        summary.update({'course_done': courses_needed == 0})
    return courses_needed


def update_ects(requirement: dict, ects: int, summary: dict) -> int:
    ects_needed = max(requirement.get('liczba_ects') - ects, 0)
    summary.update({'ects': ects_needed})
    if ects_needed > 0:
        summary.update({'fulfilled': False})
    return ects_needed


def update_alternatives(requirement: dict, student: Student, summary: dict) -> "list[dict]":
    alternatives = [get_requirement_summary(student, req) for req in requirement.get('alternatywnie')]
    summary.update({'alternatively': alternatives})
    if all([not alternative.get('fulfilled') for alternative in alternatives]):
        summary.update({'fulfilled': False})
    return alternatives


def get_requirement_summary(student: Student, requirement: dict) -> dict:
    summary = {'fulfilled': True, 'name': requirement.get('nazwa')}

    course_types = update_course_types(requirement, summary)
    course_tags = update_course_tags(requirement, summary)
    course_languages = update_course_languages(requirement, summary)
    count, ects = CompletedCourses.get_count_and_ects(student, course_types, course_tags, course_languages)

    if 'dodatkowe_info' in requirement:
        update_additional_info(requirement, summary)
    if 'liczba_przedmiotow' in requirement:
        update_courses(requirement, count, summary)
    if 'liczba_ects' in requirement:
        update_ects(requirement, ects, summary)
    if 'alternatywnie' in requirement:
        update_alternatives(requirement, student, summary)

    return summary


@student_required
def my_studies(request):
    """User studies page.

    The page displays user progress in graduating the university.
    """
    student: Student = request.user.student
    data = {'student': student, 'semester': Semester.get_upcoming_semester()}

    variant = Variant.objects.filter(program=student.program).first()
    if variant:
        requirements: list[dict] = variant.requirements.get('wymagania')
        summaries = [get_requirement_summary(student, requirement) for requirement in requirements]
        data.update({'requirements': summaries})

    return render(request, 'my_studies.html', data)

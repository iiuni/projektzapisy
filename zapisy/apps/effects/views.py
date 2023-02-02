import logging

from django.shortcuts import render

from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.models.tag import Tag as CourseTag
from apps.effects.models import CompletedCourses, Variant
from apps.users.decorators import student_required

from .models import Student

logger = logging.getLogger()


def get_requirement_summary(student: Student, requirement: dict) -> dict:
    summary = {'fulfilled': True}
    if 'dodatkowe_info' in requirement:
        summary.update({'additional_info': requirement.get('dodatkowe_info')})

    course_types, course_tags = None, None
    if 'typy_przedmiotow' in requirement:
        summary.update({'types': requirement.get('typy_przedmiotow')})
        course_types = CourseType.objects.filter(short_name__in=requirement.get('typy_przedmiotow'))
    if 'tagi_przedmiotow' in requirement:
        summary.update({'tags': requirement.get('tagi_przedmiotow')})
        course_tags = CourseTag.objects.filter(short_name__in=requirement.get('tagi_przedmiotow'))

    courses, ects = CompletedCourses.get_count_and_ects_by_types_and_tags(student, course_types, course_tags)
    if 'liczba_przedmiotow' in requirement:
        courses_needed = max(requirement.get('liczba_przedmiotow') - courses, 0)
        summary.update({'courses': courses_needed})
        if courses_needed > 0:
            summary.update({'fulfilled': False})
        if requirement.get('liczba_przedmiotow') == 1:
            summary.update({'course_done': courses_needed == 0})
    if 'liczba_ects' in requirement:
        ects_needed = max(requirement.get('liczba_ects') - ects, 0)
        summary.update({'ects': ects_needed})
        if ects_needed > 0:
            summary.update({'fulfilled': False})
    if 'jezyk_wykladowy' in requirement:
        # TODO
        pass
    if 'alternatywnie' in requirement:
        alternatives = [get_requirement_summary(student, requirement)
                        for requirement in requirement.get('alternatywnie')]
        summary.update(min(alternatives, key=lambda alt: alt['ects'] if 'ects' in alt else alt['courses']))

    summary.update({'name': requirement.get('nazwa')})
    return summary


@student_required
def my_studies(request):
    """User studies page.

    The page displays user progress in graduating the university.
    """
    data = {'requirements': []}
    student: Student = request.user.student

    variant = Variant.objects.filter(program=student.program).first()
    requirements: list[dict] = variant.requirements.get('wymagania')
    for requirement in requirements:
        requirement_summary = get_requirement_summary(student, requirement)
        data.get('requirements').append(requirement_summary)

    return render(request, 'my_studies.html', data)

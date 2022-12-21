import logging
import json
import os

from django.shortcuts import render

from apps.enrollment.courses.models.course_type import Type as CourseType
from apps.enrollment.courses.models.tag import Tag as CourseTag
from apps.effects.models import CompletedCourses
from apps.users.decorators import student_required

from .models import Student

logger = logging.getLogger()


@student_required
def my_studies(request):
    """User studies page.

    The page displays user progress in graduating the university.
    """
    data = {'requirements': []}
    student: Student = request.user.student

    # TODO: Check student program and choose corresponding requirements data

    with open(os.path.join(os.path.dirname(__file__), 'inf1stlic.json')) as requirements_file:
        requirements_data = json.load(requirements_file)
        requirements = requirements_data['wymagania']
        for requirement in requirements:
            requirement_summary = {
                'description': requirement['nazwa'],
                'fulfilled': 'Tak'
            }

            if 'dodatkowe_info' in requirement:
                requirement_summary.update({'additional_info': requirement['dodatkowe_info']})

            course_types, course_tags = None, None
            if 'typy_przedmiotow' in requirement:
                course_types = CourseType.objects.filter(short_name__in=requirement['typy_przedmiotow'])
            if 'tagi_przedmiotow' in requirement:
                course_tags = CourseTag.objects.filter(short_name__in=requirement['tagi_przedmiotow'])

            courses, ects = CompletedCourses.get_count_and_ects_by_types_and_tags(student, course_types, course_tags)
            if 'liczba_przedmiotow' in requirement:
                courses_needed = max(requirement['liczba_przedmiotow'] - courses, 0)
                requirement_summary.update({'courses': courses_needed})
                if courses_needed > 0:
                    requirement_summary.update({'fulfilled': 'Nie'})
                if requirement['liczba_przedmiotow'] == 1:
                    requirement_summary.update({'course_done': courses_needed == 0})
            if 'liczba_ects' in requirement:
                ects_needed = max(requirement['liczba_ects'] - ects, 0)
                requirement_summary.update({'ects': ects_needed})
                if ects_needed > 0:
                    requirement_summary.update({'fulfilled': 'Nie'})

            data['requirements'].append(requirement_summary)

    return render(request, 'my_studies.html', data)

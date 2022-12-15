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
    """User profile page.

    The profile page displays user settings (e-mail address, notifications). If
    he is a student, his opening times will be displayed. If the user is an
    employee, the page allows him to modify his public information (office,
    consultations).
    """
    data = {}
    student: Student = request.user.student

    with open(os.path.join(os.path.dirname(__file__), 'inf1stlic.json')) as requirements_file:
        requirements_data = json.load(requirements_file)
        requirements = requirements_data['wymagania']
        example_requirement = requirements[4]
        course_types = CourseType.objects.filter(short_name__in=example_requirement['typy_przedmiotow'])
        course_tags = CourseTag.objects.filter(short_name__in=example_requirement['tagi_przedmiotow'])
        count, ects = CompletedCourses.get_count_and_ects_by_types_and_tags(student, course_types, course_tags)
        courses_needed = example_requirement['liczba_przedmiotow'] - count
        ects_needed = example_requirement['liczba_ects'] - ects
        data.update(
            {
                'requirements': [
                    {
                        'description': example_requirement['nazwa'],
                        'courses': max(courses_needed, 0),
                        'ects': max(ects_needed, 0),
                    }
                ]
            }
        )

    return render(request, 'my_studies.html', data)

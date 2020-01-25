from django.urls import reverse
from django.db.models import QuerySet
from typing import List, Dict, Union, Any


def prepare_ajax_students_list(students: QuerySet) -> List[Dict[str, Union[str, Any]]]:
    return [{'id': s.user.id,
             'album': s.matricula,
             'recorded': True,
             'email': s.user.email,
             'name': '%s %s' % (s.user.first_name, s.user.last_name),
             'link': reverse('student-profile', args=[s.user.id])} for s in students]


def prepare_ajax_employee_list(employees: QuerySet) -> List[Dict[str, Union[str, Any]]]:
    return [{'id': e.user.id,
             'email': e.user.email,
             'name': '%s %s' % (e.user.first_name, e.user.last_name),
             'link': reverse('employee-profile', args=[e.user.id]),
             'short_old': e.user.first_name[:2] + e.user.last_name[:2],
             'short_new': e.user.first_name[:1] + e.user.last_name[:2]} for e in employees]


def prepare_students_list(students: QuerySet) -> dict:
    students_data = {}
    for student in students:
        students_data.update({student.pk: {"last_name": student.user.last_name,
                                           "first_name": student.user.first_name,
                                           "id": student.user.id,
                                           "album": student.matricula,
                                           "email": student.user.email
                                           }})
    return students_data


def prepare_employee_list(employees: QuerySet) -> dict:
    employees_data = {}
    for employee in employees:
        employees_data.update({employee.pk: {"last_name": employee.user.last_name,
                                             "first_name": employee.user.first_name,
                                             "id": employee.user.id,
                                             "email": employee.user.email
                                             }})
    return employees_data

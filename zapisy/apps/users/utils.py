from django.urls import reverse
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.db.models import QuerySet
from typing import List, Dict, Union, Any
from rest_framework.request import Request


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


class StaffPermission(BasePermission):
    message = 'Only for staff members'

    def has_permission(self, request: Request, view: Any) -> bool:
        return bool(request.method in SAFE_METHODS and request.user.is_staff)

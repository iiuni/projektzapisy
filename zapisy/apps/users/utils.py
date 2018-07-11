from django.urls import reverse
from rest_framework.permissions import BasePermission, SAFE_METHODS


def prepare_ajax_students_list(students):
    return [{'id': s.user.id,
             'album': s.matricula,
             'recorded': True,
             'email': s.user.email,
             'name': '%s %s' % (s.user.first_name, s.user.last_name),
             'link': reverse('student-profile', args=[s.user.id])} for s in students]


def prepare_ajax_employee_list(employees):
    return [{'id': e.user.id,
             'email': e.user.email,
             'name': '%s %s' % (e.user.first_name, e.user.last_name),
             'link': reverse('employee-profile', args=[e.user.id]),
             'short_old': e.user.first_name[:2] + e.user.last_name[:2],
             'short_new': e.user.first_name[:1] + e.user.last_name[:2]} for e in employees]


class StaffPermission(BasePermission):
    message = 'Only for staff members'

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS and request.user.is_staff)

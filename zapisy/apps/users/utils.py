# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse


def prepare_ajax_students_list(students):
    return map(lambda s:
               {'id': s.user.id,
                'album': s.matricula,
                'recorded': True,
                'email': s.user.email,
                'name': u'%s %s' % (s.user.first_name, s.user.last_name),
                'link': reverse('student-profile', args=[s.user.id])}, students)


def prepare_ajax_employee_list(employees):
    return map(lambda e:
               {'id': e.user.id,
                'email': e.user.email,
                'name': u'%s %s' % (e.user.first_name, e.user.last_name),
                'link': reverse('employee-profile', args=[e.user.id]),
                'short_old': e.user.first_name[:2] + e.user.last_name[:2],
                'short_new': e.user.first_name[:1] + e.user.last_name[:2]},
               employees)

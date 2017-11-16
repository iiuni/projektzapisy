# -*- coding: utf-8 -*-

from django.test import TestCase

from apps.schedule.forms import EventForm
from apps.users.tests.factories import UserProfileFactory, UserFactory, EmployeeFactory


class EventFormTestCase(TestCase):
    def test_event_form_accepts_blank_description_when_user_is_employee(self):
        e = EmployeeFactory()
        UserProfileFactory(user=e.user, is_employee=True)
        data = {'description': ''}
        form = EventForm(e.user, data)
        self.assertTrue(form.is_valid())

    def test_event_form_accepts_blank_description_when_user_is_student(self):
        user = UserFactory()
        UserProfileFactory(user=user, is_student=True, is_employee=False)
        data = {'description': ''}
        form = EventForm(user, data)
        self.assertTrue(form.is_valid())

from django.test import TestCase
from .factories import EmployeeFactory, StudentFactory
from django.core.urlresolvers import reverse
from apps.enrollment.courses.tests.factories import SemesterFactory

class IcalExportTest(TestCase):
    def setUp(self):
        # We'll need an existing active semester
        SemesterFactory()

    def _test_ical_for_user(self, user):
        self.client.force_login(user)
        response = self.client.get(reverse('ical'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/calendar')
        self.assertTrue('attachment' in response['Content-Disposition'])

    def test_student_ical_export(self):
        s = StudentFactory()
        self._test_ical_for_user(s.user)

    def test_employee_ical_export(self):
        e = EmployeeFactory()
        self._test_ical_for_user(e.user)

"""Tests for module computing the opening times.

The generation itself has been tested to comply to the previously used SQL
functions. This tests will verify, that the functions use the data correctly.
"""
from datetime import timedelta

from django.test import TestCase

from apps.enrollment.courses.models import Group, Semester
from apps.enrollment.records.models import T0Times
from apps.users.models import Student


class PopulateT0Test(TestCase):
    """To understand the test scenario see the fixture."""
    fixtures = ['students_populate_t0.yaml']

    @classmethod
    def setUpTestData(cls):
        """Computes GroupOpeningTimes for all tests."""
        cls.semester = Semester.objects.get(pk=1)
        cls.bolek = Student.objects.get(pk=1)
        cls.lolek = Student.objects.get(pk=2)
        cls.tosia = Student.objects.get(pk=3)
        cls.zosia = Student.objects.get(pk=4)

        T0Times.populate_t0(cls.semester)

    def test_t0_times_equal_ammount_of_ects(self):
        """Tests that students with the same ammount of ECTS have equal t0 times."""
        bolek_t0_opening = T0Times.objects.get(
            student=self.bolek, semester=self.semester).time
        lolek_t0_opening = T0Times.objects.get(
            student=self.lolek, semester=self.semester).time
        assert bolek_t0_opening == lolek_t0_opening

    def test_t0_times_order(self):
        """Tests that checks if t0 times is in correct oreder and correct intervals."""
        groups_spacing = self.semester.records_pause
        global_t0_opening = self.semester.records_opening - timedelta(hours=2)

        bolek_t0_opening = T0Times.objects.get(
            student=self.bolek, semester=self.semester).time
        lolek_t0_opening = T0Times.objects.get(
            student=self.lolek, semester=self.semester).time
        tosia_t0_opening = T0Times.objects.get(
            student=self.tosia, semester=self.semester).time
        zosia_t0_opening = T0Times.objects.get(
            student=self.zosia, semester=self.semester).time

        assert global_t0_opening == tosia_t0_opening  # tosia has the fewest ECTS in the group
        assert tosia_t0_opening - bolek_t0_opening == timedelta(minutes=groups_spacing)
        assert tosia_t0_opening - zosia_t0_opening == timedelta(minutes=groups_spacing) * 2
        assert lolek_t0_opening - zosia_t0_opening == timedelta(minutes=groups_spacing)

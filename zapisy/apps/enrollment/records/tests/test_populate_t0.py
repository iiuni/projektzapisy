"""Tests for module computing the opening times.

The generation itself has been tested to comply to the previously used SQL
functions. This tests will verify, that the functions use the data correctly.
"""
from datetime import timedelta

from django.test import TestCase

from apps.enrollment.courses.models import Semester
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
        cls.marek = Student.objects.get(pk=5)

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
        groups_spacing = self.semester.records_interval_as_timedelta
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
        assert tosia_t0_opening - bolek_t0_opening == groups_spacing
        assert tosia_t0_opening - zosia_t0_opening == groups_spacing * 2
        assert lolek_t0_opening - zosia_t0_opening == groups_spacing

    def test_maximum_interval_between_records(self):
        """Checks that the maximum interval between records is at most 'groups_spacing'."""
        groups_spacing = self.semester.records_interval_as_timedelta

        bolek_t0_opening = T0Times.objects.get(
            student=self.bolek, semester=self.semester).time
        lolek_t0_opening = T0Times.objects.get(
            student=self.lolek, semester=self.semester).time
        tosia_t0_opening = T0Times.objects.get(
            student=self.tosia, semester=self.semester).time
        zosia_t0_opening = T0Times.objects.get(
            student=self.zosia, semester=self.semester).time
        marek_t0_opening = T0Times.objects.get(
            student=self.marek, semester=self.semester).time

        t0_openings = sorted([
            bolek_t0_opening,
            lolek_t0_opening,
            tosia_t0_opening,
            zosia_t0_opening,
            marek_t0_opening,
        ])

        maximum = max([x[1] - x[0] for x in zip(t0_openings[:-1], t0_openings[1:])])

        assert maximum == groups_spacing

    def test_records_not_fall_in_the_nighttime(self):
        """Checks whether the mechanism to prevent recordings from starting at night."""
        bolek_pozny_headstart = timedelta(hours=13)
        lolek_pozny_headstart = timedelta(hours=24, minutes=1)

        bolek_pozny_t0_opening = self.semester.records_opening - bolek_pozny_headstart
        lolek_pozny_t0_opening = self.semester.records_opening - lolek_pozny_headstart

        moved_bolek_pozny = bolek_pozny_t0_opening - T0Times.prevent_nighttime_t0(bolek_pozny_headstart)
        moved_lolek_pozny = lolek_pozny_t0_opening - T0Times.prevent_nighttime_t0(lolek_pozny_headstart)

        assert moved_bolek_pozny == bolek_pozny_t0_opening - timedelta(hours=12)
        assert moved_lolek_pozny == lolek_pozny_t0_opening - timedelta(hours=24)

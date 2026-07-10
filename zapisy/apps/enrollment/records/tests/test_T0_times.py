"""Tests for module computing T0 times for students."""
from datetime import timedelta

from django.test import TestCase
from django.conf import settings

from apps.enrollment.courses.models import Semester
from apps.enrollment.records.models import T0Times
from apps.users.models import Student


class T0TimeTest(TestCase):
    """To understand the test scenario see the fixture."""
    fixtures = ['t0_students.yaml']

    @classmethod
    def setUpTestData(cls):
        """Computes TOTimes for all tests."""
        cls.semester = Semester.objects.get(pk=1)
        cls.bolek = Student.objects.get(pk=1)
        cls.lola = Student.objects.get(pk=2)

        T0Times.populate_t0(cls.semester)

    def test_T0_population(self):
        """Tests that T0 times were correctly calculated for students.

        Bolek is studying a native program thus he receives extra time
        bonus based on his ECTS points (He has 1). Lola is studying an external
        program and receives no bonuses.
        """
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        lola_t0 = T0Times.objects.get(student=self.lola, semester=self.semester).time
        assert lola_t0 - bolek_t0 == timedelta(minutes=settings.ECTS_BONUS)

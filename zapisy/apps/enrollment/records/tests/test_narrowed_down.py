"""Tests for computing the opening times in special cases."""
from datetime import timedelta

from django.test import TestCase

from apps.enrollment.courses.models import Group, Semester
from apps.enrollment.records.models import GroupOpeningTimes, T0Times
from apps.offer.vote.models.single_vote import SingleVote
from apps.users.models import Student


class OpeningTimesTest(TestCase):
    """To understand the test scenario see the fixture."""
    fixtures = ['new_semester.yaml']

    @classmethod
    def setUpTestData(cls):
        """Computes GroupOpeningTimes for all tests."""
        cls.semester = Semester.objects.get(pk=1)
        cls.bolek = Student.objects.get(pk=1)
        cls.lolek = Student.objects.get(pk=2)
        cls.tola = Student.objects.get(pk=3)

        cls.knitting_lecture_group = Group.objects.get(pk=11)
        
        #Populate opening times for knitting lecture.
        GroupOpeningTimes.populate_opening_times(cls.semester, groups=[self.knitting_lecture_group])
        
        tola_knitting_opening = GroupOpeningTimes.objects.get(
            student=cls.tola, group=cls.knitting_lecture_group).time
        lolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=cls.lolek, group=cls.knitting_lecture_group).time
        cls.diff = lolek_knitting_opening - tola_knitting_opening
        
        #Tola gets an earlier opening time
        GroupOpeningTimes.objects.filter(student=cls.tola, group=cls.knitting_lecture_group).update(time=tola_knitting_opening + 2 * cls.diff)
        
        #Populate opening times for knitting lecture, but only for Bolek and Lolek now.
        GroupOpeningTimes.populate_opening_times(
          cls.semester, students=[self.bolek, self.lolek],
          groups=[self.knitting_lecture_group]
        )
 

    def test_selected_populated_times(self):
        """Tests that Tola's T0 hasn't changed"""

        tola_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.tola, group=self.knitting_lecture_group).time
        lolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.lolek, group=self.knitting_lecture_group).time
        assert bolek_knitting_opening - lolek_knitting_opening == 2 * self.diff

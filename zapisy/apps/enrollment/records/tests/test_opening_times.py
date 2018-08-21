"""Tests for module computing the opening times.

The generation itself has been tested to comply to the previously used SQL
functions. This tests will verify, that the functions use the data correctly.
"""
from datetime import timedelta

from django.test import TestCase

from apps.enrollment.records.models import T0Times, GroupOpeningTimes
from apps.enrollment.courses.models import Semester, Group
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
        GroupOpeningTimes.populate_opening_times(cls.semester)

    def test_populated_times(self):
        """Tests, that GroupOpeningTimes are correctly based on T0 and votes."""
        knitting_lecture_group = Group.objects.get(pk=11)
        bolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.bolek, group=knitting_lecture_group).time
        lolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.lolek, group=knitting_lecture_group).time
        assert bolek_knitting_opening - lolek_knitting_opening == timedelta(hours=1)

    def test_group_openings(self):
        """Tests, that the functions correctly assert the group opened or closed.

        We look at Bolek's T0 and his votes. He only gets as many bonus days, as
        he did provide votes for the course.
        """
        knitting_lecture_group = Group.objects.get(pk=11)
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        bolek_votes_for_knitting = SingleVote.objects.get(
            student=self.bolek, course=knitting_lecture_group.course).correction
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek,
            knitting_lecture_group,
            bolek_t0 - timedelta(days=bolek_votes_for_knitting) - timedelta(seconds=5))
        assert GroupOpeningTimes.is_group_open_for_student(
            self.bolek, knitting_lecture_group, bolek_t0 - timedelta(days=bolek_votes_for_knitting))

    def test_records_end(self):
        """Tests, that student will not be able to enroll after records are
        closed.
        """
        knitting_lecture_group = Group.objects.get(pk=11)
        assert GroupOpeningTimes.is_group_open_for_student(self.bolek, knitting_lecture_group,
                                                           self.semester.records_closing)
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek,
            knitting_lecture_group,
            self.semester.records_closing + timedelta(seconds=5))

    def test_group_own_record_times(self):
        """If a course has its own opening time and it was not participating in
        voting, its time should take precedence over T0s.
        """
        washing_up_seminar_group = Group.objects.get(pk=22)
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek, washing_up_seminar_group, bolek_t0 - timedelta(seconds=5))
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek, washing_up_seminar_group, bolek_t0 + timedelta(seconds=5))
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek,
            washing_up_seminar_group,
            washing_up_seminar_group.course.records_start - timedelta(seconds=5))
        assert GroupOpeningTimes.is_group_open_for_student(
            self.bolek,
            washing_up_seminar_group,
            washing_up_seminar_group.course.records_start + timedelta(seconds=1))
        assert GroupOpeningTimes.is_group_open_for_student(
            self.bolek, washing_up_seminar_group, washing_up_seminar_group.course.records_end)
        assert not GroupOpeningTimes.is_group_open_for_student(
            self.bolek,
            washing_up_seminar_group,
            washing_up_seminar_group.course.records_end + timedelta(seconds=5))

    def test_plural_function(self):
        """This repeats some of the tests using `are_groups_open_for_student`.
        """
        knitting_lecture_group = Group.objects.get(pk=11)
        washing_up_seminar_group = Group.objects.get(pk=22)
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        bolek_votes_for_knitting = SingleVote.objects.get(
            student=self.bolek, course=knitting_lecture_group.course).correction
        assert not GroupOpeningTimes.are_groups_open_for_student(
            self.bolek, [knitting_lecture_group],
            bolek_t0 - timedelta(days=bolek_votes_for_knitting) -
            timedelta(seconds=5))[knitting_lecture_group.id]
        assert GroupOpeningTimes.are_groups_open_for_student(
            self.bolek, [knitting_lecture_group],
            bolek_t0 - timedelta(days=bolek_votes_for_knitting))[knitting_lecture_group.id]
        assert not GroupOpeningTimes.are_groups_open_for_student(
            self.bolek, [washing_up_seminar_group],
            washing_up_seminar_group.course.records_start -
            timedelta(seconds=5))[washing_up_seminar_group.id]
        assert GroupOpeningTimes.are_groups_open_for_student(
            self.bolek, [washing_up_seminar_group],
            washing_up_seminar_group.course.records_start +
            timedelta(seconds=1))[washing_up_seminar_group.id]

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

        cls.knitting_lecture_group = Group.objects.get(pk=11)
        cls.washing_up_seminar_group = Group.objects.get(pk=22)

        GroupOpeningTimes.populate_opening_times(cls.semester)

    def test_populated_times(self):
        """Tests, that GroupOpeningTimes are correctly based on T0 and votes."""
        bolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.bolek, group=self.knitting_lecture_group).time
        lolek_knitting_opening = GroupOpeningTimes.objects.get(
            student=self.lolek, group=self.knitting_lecture_group).time
        assert bolek_knitting_opening - lolek_knitting_opening == timedelta(hours=1)

    def test_group_openings(self):
        """Tests, that the functions correctly assert the group opened or closed.

        We look at Bolek's T0 and his votes. He only gets as many bonus days, as
        he did provide votes for the course.
        """
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        bolek_votes_for_knitting = SingleVote.objects.get(
            student=self.bolek,
            proposal=self.knitting_lecture_group.course.entity.courseinformation.pk).correction
        bolek_knitting_group_opening = bolek_t0 - timedelta(days=bolek_votes_for_knitting)
        self.assertFalse(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.knitting_lecture_group,
                bolek_knitting_group_opening - timedelta(seconds=5)))
        self.assertTrue(
            GroupOpeningTimes.is_group_open_for_student(self.bolek, self.knitting_lecture_group,
                                                        bolek_knitting_group_opening))

    def test_records_end(self):
        """Tests, that student will not be able to enroll after records are
        closed.
        """
        self.assertTrue(
            GroupOpeningTimes.is_group_open_for_student(self.bolek, self.knitting_lecture_group,
                                                        self.semester.records_closing))
        self.assertFalse(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.knitting_lecture_group,
                self.semester.records_closing + timedelta(seconds=5)))

    def test_group_own_record_times(self):
        """If a course has its own opening time and it was not participating in
        voting, its time should take precedence over T0s.
        """
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        self.assertFalse(
            GroupOpeningTimes.is_group_open_for_student(self.bolek, self.washing_up_seminar_group,
                                                        bolek_t0 - timedelta(seconds=5)))
        self.assertFalse(GroupOpeningTimes.is_group_open_for_student(
            self.bolek, self.washing_up_seminar_group, bolek_t0 + timedelta(seconds=5)))
        self.assertFalse(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.washing_up_seminar_group,
                self.washing_up_seminar_group.course.records_start - timedelta(seconds=5)))
        self.assertTrue(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.washing_up_seminar_group,
                self.washing_up_seminar_group.course.records_start + timedelta(seconds=1)))
        self.assertTrue(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.washing_up_seminar_group,
                self.washing_up_seminar_group.course.records_end))
        self.assertFalse(
            GroupOpeningTimes.is_group_open_for_student(
                self.bolek, self.washing_up_seminar_group,
                self.washing_up_seminar_group.course.records_end + timedelta(seconds=5)))

    def test_plural_function(self):
        """This repeats some of the tests using `are_groups_open_for_student`.
        """
        bolek_t0 = T0Times.objects.get(student=self.bolek, semester=self.semester).time
        bolek_votes_for_knitting = SingleVote.objects.get(
            student=self.bolek,
            proposal=self.knitting_lecture_group.course.entity.courseinformation.pk).correction

        bolek_knitting_group_opening = bolek_t0 - timedelta(days=bolek_votes_for_knitting)
        self.assertFalse(
            GroupOpeningTimes.are_groups_open_for_student(
                self.bolek, [self.knitting_lecture_group], bolek_knitting_group_opening -
                timedelta(seconds=5))[self.knitting_lecture_group.id])
        self.assertTrue(
            GroupOpeningTimes.are_groups_open_for_student(
                self.bolek, [self.knitting_lecture_group],
                bolek_knitting_group_opening)[self.knitting_lecture_group.id])
        self.assertFalse(
            GroupOpeningTimes.are_groups_open_for_student(
                self.bolek, [self.washing_up_seminar_group],
                self.washing_up_seminar_group.course.records_start -
                timedelta(seconds=5))[self.washing_up_seminar_group.id])
        self.assertTrue(
            GroupOpeningTimes.are_groups_open_for_student(
                self.bolek, [self.washing_up_seminar_group],
                self.washing_up_seminar_group.course.records_start +
                timedelta(seconds=1))[self.washing_up_seminar_group.id])

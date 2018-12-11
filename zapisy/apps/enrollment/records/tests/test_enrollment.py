"""Tests for enrolling and enqueuing students."""
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.enrollment.records.models import Record, RecordStatus, GroupOpeningTimes
from apps.enrollment.courses.models import Semester, Group, StudentPointsView
from apps.users.models import Student


def mock_datetime(year, month, day, hour=0, minute=0):
    """Mock datetime used to model performing operations at a particular time.

    This is a meta-function. It will return a class inheriting from datetime and
    overriding its `now` function.
    """
    timestamp = datetime(year, month, day, hour, minute)

    class MockDateTime(datetime):
        """Override of datetime."""

        @classmethod
        def now(cls, _=None):
            return timestamp

    return MockDateTime


# We will patch datetime for records module. This is fairly counterintuitive See
# https://docs.python.org/3/library/unittest.mock.html#where-to-patch for
# explanation.
RECORDS_DATETIME = 'apps.enrollment.records.models.records.datetime'


@override_settings(RUN_ASYNC=False)
class EnrollmentTest(TestCase):
    """Verify correctness of our enrollment logic implementation.

    The tests are missing one important issue — the asynchronous task queue. To
    make testing easier, the test will run all tasks synchronously (eagerly).
    """
    fixtures = ['new_semester.yaml']

    @classmethod
    def setUpTestData(cls):
        """Computes GroupOpeningTimes for all tests."""
        cls.semester = Semester.objects.get(pk=1)
        cls.bolek = Student.objects.get(pk=1)
        cls.lolek = Student.objects.get(pk=2)
        cls.tola = Student.objects.get(pk=3)
        GroupOpeningTimes.populate_opening_times(cls.semester)

    def test_simple_enrollment(self):
        """Bolek will just enqueue into the group."""
        knitting_lecture_group = Group.objects.get(pk=11)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, knitting_lecture_group)

        assert Record.objects.filter(
            student=self.bolek, group=knitting_lecture_group,
            status=RecordStatus.ENROLLED).exists()

    def test_lecture_group_also_enrolled(self):
        """Bolek will just enqueue into the exercises group. He should also be
        enrolled into the lecture."""
        cooking_lecture_group = Group.objects.get(pk=31)
        cooking_exercise_group = Group.objects.get(pk=32)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_exercise_group)

        assert Record.objects.filter(
            student=self.bolek, group=cooking_exercise_group,
            status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()

    def test_exercise_group_also_removed(self):
        """Like above bolek will enqueue into exercise group. Then he'll leave.

        He first should be automatically pulled into the lecture group. Then he
        will unenroll from the lecture group and he should be removed from the
        exercise group as well.
        """
        cooking_lecture_group = Group.objects.get(pk=31)
        cooking_exercise_group = Group.objects.get(pk=32)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_exercise_group)

        assert Record.objects.filter(
            student=self.bolek, group=cooking_exercise_group,
            status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 2, 12)):
            assert Record.remove_from_group(self.bolek, cooking_lecture_group)

        assert not Record.objects.filter(
            student=self.bolek, group=cooking_exercise_group,
            status=RecordStatus.ENROLLED).exists()
        assert not Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()

    def test_bolek_comes_before_lolek(self):
        """Bolek will be first to enroll into the groups. Lolek will remain in
        the queue of the exercise group, yet he will fit in the lecture
        group."""
        cooking_lecture_group = Group.objects.get(pk=31)
        cooking_exercise_group = Group.objects.get(pk=32)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_exercise_group)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12, 1)):
            assert Record.enqueue_student(self.lolek, cooking_exercise_group)

        assert Record.objects.filter(
            student=self.bolek, group=cooking_exercise_group,
            status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()
        assert not Record.objects.filter(
            student=self.lolek, group=cooking_exercise_group,
            status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.lolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.lolek, group=cooking_exercise_group, status=RecordStatus.QUEUED).exists()
        assert not Record.objects.filter(
            student=self.lolek, group=cooking_lecture_group, status=RecordStatus.QUEUED).exists()

    def test_student_autoremoved_from_group(self):
        """Bolek switches seminar group for "Mycie Naczyń".

        In the meantime, Lolek tries to join the first group. He waits in queue,
        but is pulled in when Bolek leaves a vacancy.
        """
        washing_up_seminar_1 = Group.objects.get(pk=21)
        washing_up_seminar_2 = Group.objects.get(pk=22)

        # Bolek joins group 1.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12)):
            assert Record.enqueue_student(self.bolek, washing_up_seminar_1)
        assert Record.objects.filter(
            student=self.bolek, group=washing_up_seminar_1, status=RecordStatus.ENROLLED).exists()

        # Lolek tries to join group 1 and is enqueued.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12)):
            assert Record.enqueue_student(self.lolek, washing_up_seminar_1)
        assert not Record.objects.filter(
            student=self.lolek, group=washing_up_seminar_1, status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.lolek, group=washing_up_seminar_1, status=RecordStatus.QUEUED).exists()

        # Bolek switches the group.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12, 5)):
            assert Record.enqueue_student(self.bolek, washing_up_seminar_2)
        assert Record.objects.filter(
            student=self.bolek, group=washing_up_seminar_2, status=RecordStatus.ENROLLED).exists()
        assert not Record.objects.filter(
            student=self.bolek, group=washing_up_seminar_1, status=RecordStatus.ENROLLED).exists()

        # Lolek should be pulled in.
        assert Record.objects.filter(
            student=self.lolek, group=washing_up_seminar_1, status=RecordStatus.ENROLLED).exists()
        assert not Record.objects.filter(
            student=self.lolek, group=washing_up_seminar_1, status=RecordStatus.QUEUED).exists()

    def test_student_exceeds_the_35_limit(self):
        """Bolek will try to sign up to "Gotowanie" and "Szydełkowanie" before
        35 points limit abolition. He should be successful with "Gotowanie",
        which costs exactly 35 ECTS, but not with the second enrollment.
        """
        knitting_lecture_group = Group.objects.get(pk=11)
        cooking_lecture_group = Group.objects.get(pk=31)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_lecture_group)
        assert Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()
        assert StudentPointsView.student_points_in_semester(self.bolek, self.semester) == 35

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12, 5)):
            # He should be able to join the queue.
            assert Record.enqueue_student(self.bolek, knitting_lecture_group)
        # His enrollment with "Gotowanie" should still exist.
        assert Record.objects.filter(
            student=self.bolek, group=cooking_lecture_group, status=RecordStatus.ENROLLED).exists()
        # His record with "Szydełkowanie" should be removed.
        assert not Record.objects.filter(
            student=self.bolek, group=knitting_lecture_group,
            status=RecordStatus.ENROLLED).exists()
        assert Record.objects.filter(
            student=self.bolek, group=knitting_lecture_group, status=RecordStatus.REMOVED).exists()
        assert StudentPointsView.student_points_in_semester(self.bolek, self.semester) == 35

    def test_higher_priority_1(self):
        """Both exercise groups are occupied by Bolek and Lolek. Tola will
        enqueue to both with different priorities. She will end up in the group
        of higher priority regardless of the order in which Bolek and Lolek free
        up the places.
        """
        cooking_exercise_1 = Group.objects.get(pk=32)
        cooking_exercise_2 = Group.objects.get(pk=33)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_exercise_1)
            assert Record.enqueue_student(self.lolek, cooking_exercise_2)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 13)):
            assert Record.enqueue_student(self.tola, cooking_exercise_1)
            assert Record.set_queue_priority(self.tola, cooking_exercise_1, 7)
            assert Record.enqueue_student(self.tola, cooking_exercise_2)
            assert Record.set_queue_priority(self.tola, cooking_exercise_2, 8)

        assert Record.is_recorded(self.tola.pk, cooking_exercise_1.pk)
        assert Record.is_recorded(self.tola.pk, cooking_exercise_2.pk)
        assert not Record.is_enrolled(self.tola.pk, cooking_exercise_1.pk)
        assert not Record.is_enrolled(self.tola.pk, cooking_exercise_2.pk)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 12)):
            assert Record.remove_from_group(self.bolek,
                                            cooking_exercise_1) == [cooking_exercise_1.pk]
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 13)):
            assert Record.remove_from_group(self.lolek,
                                            cooking_exercise_2) == [cooking_exercise_2.pk]

        assert not Record.is_recorded(self.tola.pk, cooking_exercise_1.pk)
        assert Record.is_enrolled(self.tola.pk, cooking_exercise_2.pk)

    def test_higher_priority_2(self):
        """The only difference between this test and the one above is the order
        in which Bolek and Lolek leave their groups.
        """
        cooking_exercise_1 = Group.objects.get(pk=32)
        cooking_exercise_2 = Group.objects.get(pk=33)
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            assert Record.enqueue_student(self.bolek, cooking_exercise_1)
            assert Record.enqueue_student(self.lolek, cooking_exercise_2)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 13)):
            assert Record.enqueue_student(self.tola, cooking_exercise_1)
            assert Record.set_queue_priority(self.tola, cooking_exercise_1, 7)
            assert Record.enqueue_student(self.tola, cooking_exercise_2)
            assert Record.set_queue_priority(self.tola, cooking_exercise_2, 8)

        assert Record.is_recorded(self.tola.pk, cooking_exercise_1.pk)
        assert Record.is_recorded(self.tola.pk, cooking_exercise_2.pk)
        assert not Record.is_enrolled(self.tola.pk, cooking_exercise_1.pk)
        assert not Record.is_enrolled(self.tola.pk, cooking_exercise_2.pk)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 12)):
            assert Record.remove_from_group(self.lolek,
                                            cooking_exercise_2) == [cooking_exercise_2.pk]
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 13)):
            assert Record.remove_from_group(self.bolek,
                                            cooking_exercise_1) == [cooking_exercise_1.pk]

        assert not Record.is_recorded(self.tola.pk, cooking_exercise_1.pk)
        assert Record.is_enrolled(self.tola.pk, cooking_exercise_2.pk)

"""Tests for enrolling and enqueuing students."""
from datetime import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.enrollment.courses.models import Group, Semester
from apps.enrollment.records.models import GroupOpeningTimes, Record, RecordStatus
from apps.enrollment.records import engine
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

        @classmethod
        def today(cls):
            return cls.now()

    return MockDateTime


# We will patch datetime for records module. This is fairly counterintuitive See
# https://docs.python.org/3/library/unittest.mock.html#where-to-patch for
# explanation.
SEMESTER_DATETIME = 'apps.enrollment.courses.models.semester.datetime'
ENGINE_DATETIME = 'apps.enrollment.records.engine.fillup_group.datetime'
RECORDS_DATETIME = 'apps.enrollment.records.engine.enqueue.datetime'


@override_settings(RUN_ASYNC=False)
@patch(SEMESTER_DATETIME, mock_datetime(2011, 10, 4))
@patch(ENGINE_DATETIME, mock_datetime(2011, 10, 4))
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

        cls.knitting_lecture_group = Group.objects.get(pk=11)
        cls.washing_up_seminar_1 = Group.objects.get(pk=21)
        cls.washing_up_seminar_2 = Group.objects.get(pk=22)
        cls.cooking_lecture_group = Group.objects.get(pk=31)
        cls.cooking_exercise_group_1 = Group.objects.get(pk=32)
        cls.cooking_exercise_group_2 = Group.objects.get(pk=33)
        cls.cleaning_lecture_group = Group.objects.get(pk=41)
        cls.cleaning_exercise_group_1 = Group.objects.get(pk=42)
        cls.cleaning_exercise_group_2 = Group.objects.get(pk=43)

        GroupOpeningTimes.populate_opening_times(cls.semester)

    def test_simple_enrollment(self):
        """Bolek will just enqueue into the group."""
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.knitting_lecture_group))

        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.knitting_lecture_group,
                status=RecordStatus.ENROLLED).exists())

    def test_bolek_comes_before_lolek(self):
        """Tests that the group limits are respected.

        Bolek will be first to enroll into the groups. Lolek will remain in the
        queue of the exercise group.
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.cooking_exercise_group_1))
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12, 1)):
            self.assertTrue(engine.enqueue_student(self.lolek, self.cooking_exercise_group_1))

        self.assertTrue(
            Record.objects.filter(
                student=self.bolek,
                group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertFalse(
            Record.objects.filter(
                student=self.bolek, group=self.cooking_lecture_group,
                status=RecordStatus.ENROLLED).exists())
        self.assertFalse(
            Record.objects.filter(
                student=self.lolek,
                group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertTrue(
            Record.objects.filter(
                student=self.lolek, group=self.cooking_exercise_group_1,
                status=RecordStatus.QUEUED).exists())

    def test_student_autoremoved_from_group(self):
        """Bolek switches seminar group for "Mycie Naczyń".

        In the meantime, Lolek tries to join the first group. He waits in queue,
        but is pulled in when Bolek leaves a vacancy.
        """
        # Bolek joins group 1.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.washing_up_seminar_1))
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.washing_up_seminar_1,
                status=RecordStatus.ENROLLED).exists())

        # Lolek tries to join group 1 and is enqueued.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12)):
            self.assertTrue(engine.enqueue_student(self.lolek, self.washing_up_seminar_1))
        self.assertFalse(
            Record.objects.filter(
                student=self.lolek, group=self.washing_up_seminar_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertTrue(
            Record.objects.filter(
                student=self.lolek, group=self.washing_up_seminar_1,
                status=RecordStatus.QUEUED).exists())

        # Bolek switches the group.
        with patch(RECORDS_DATETIME, mock_datetime(2011, 12, 5, 12, 5)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.washing_up_seminar_2))
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.washing_up_seminar_2,
                status=RecordStatus.ENROLLED).exists())
        self.assertFalse(
            Record.objects.filter(
                student=self.bolek, group=self.washing_up_seminar_1,
                status=RecordStatus.ENROLLED).exists())

        # Lolek should be pulled in.
        self.assertTrue(
            Record.objects.filter(
                student=self.lolek, group=self.washing_up_seminar_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertFalse(
            Record.objects.filter(
                student=self.lolek, group=self.washing_up_seminar_1,
                status=RecordStatus.QUEUED).exists())

    def test_student_exceeds_the_35_limit(self):
        """Tests the ECTS limit constraint.

        Bolek will try to sign up to "Gotowanie" and "Szydełkowanie" before
        35 points limit abolition. He should be successful with "Gotowanie",
        which costs exactly 35 ECTS, but not with the second enrollment.
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.cooking_exercise_group_1))
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertEqual(
            engine.student_points_in_semester(self.bolek, self.semester), 35)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12, 5)):
            # He should be able to join the queue.
            self.assertTrue(engine.enqueue_student(self.bolek, self.knitting_lecture_group))
        # His enrollment with "Gotowanie" should still exist.
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        # His record with "Szydełkowanie" should be removed.
        self.assertFalse(
            Record.objects.filter(
                student=self.bolek, group=self.knitting_lecture_group,
                status=RecordStatus.ENROLLED).exists())
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.knitting_lecture_group,
                status=RecordStatus.BLOCKED).exists())
        self.assertEqual(
            engine.student_points_in_semester(self.bolek, self.semester), 35)

    def test_higher_priority_1(self):
        """Tests queue priorities.

        Both exercise groups are occupied by Bolek and Lolek. Tola will enqueue
        to both with different priorities. She will end up in the group of
        higher priority regardless of the order in which Bolek and Lolek free up
        the places.
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.cooking_exercise_group_1))
            self.assertTrue(engine.enqueue_student(self.lolek, self.cooking_exercise_group_2))

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 13)):
            self.assertTrue(engine.enqueue_student(self.tola, self.cooking_exercise_group_1))
            self.assertTrue(engine.set_queue_priority(self.tola, self.cooking_exercise_group_1, 7))
            self.assertTrue(engine.enqueue_student(self.tola, self.cooking_exercise_group_2))
            self.assertTrue(engine.set_queue_priority(self.tola, self.cooking_exercise_group_2, 8))

        self.assertTrue(engine.is_recorded(self.tola, self.cooking_exercise_group_1))
        self.assertTrue(engine.is_recorded(self.tola, self.cooking_exercise_group_2))
        self.assertFalse(engine.is_enrolled(self.tola, self.cooking_exercise_group_1))
        self.assertFalse(engine.is_enrolled(self.tola, self.cooking_exercise_group_2))

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 12)):
            self.assertTrue(engine.remove_from_group(self.bolek, self.cooking_exercise_group_1))
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 13)):
            self.assertTrue(engine.remove_from_group(self.lolek, self.cooking_exercise_group_2))

        self.assertFalse(engine.is_recorded(self.tola, self.cooking_exercise_group_1))
        self.assertTrue(engine.is_enrolled(self.tola, self.cooking_exercise_group_2))

    def test_higher_priority_2(self):
        """Tests queue priorities.

        The only difference between this test and the one above is the order in
        which Bolek and Lolek leave their groups.
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.cooking_exercise_group_1))
            self.assertTrue(engine.enqueue_student(self.lolek, self.cooking_exercise_group_2))

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 1, 13)):
            self.assertTrue(engine.enqueue_student(self.tola, self.cooking_exercise_group_1))
            self.assertTrue(engine.set_queue_priority(self.tola, self.cooking_exercise_group_1, 7))
            self.assertTrue(engine.enqueue_student(self.tola, self.cooking_exercise_group_2))
            self.assertTrue(engine.set_queue_priority(self.tola, self.cooking_exercise_group_2, 8))

        self.assertTrue(engine.is_recorded(self.tola, self.cooking_exercise_group_1))
        self.assertTrue(engine.is_recorded(self.tola, self.cooking_exercise_group_2))
        self.assertFalse(engine.is_enrolled(self.tola, self.cooking_exercise_group_1))
        self.assertFalse(engine.is_enrolled(self.tola, self.cooking_exercise_group_2))

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 12)):
            self.assertTrue(engine.remove_from_group(self.lolek, self.cooking_exercise_group_2))
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 13)):
            self.assertTrue(engine.remove_from_group(self.bolek, self.cooking_exercise_group_1))

        self.assertFalse(engine.is_recorded(self.tola, self.cooking_exercise_group_1))
        self.assertTrue(engine.is_enrolled(self.tola, self.cooking_exercise_group_2))

    def test_waiting_students_number(self):
        """Check whether we get correct number of waiting students of given type.

        Our exercise groups have limit for 1 person.
        Bolek is in cooking_exercise_group_1 and Lolek is in cooking_exercise_group_2.
        Tola is in queues of all above groups.
        Bolek changed his mind and want to be in cooking_exercise_group_2.
        Lolek also want to join other group(cooking_exercise_group_1).
        We have 2 enrolled Records and 4 enqueued.
        Only Lola isn't enrolled in any group.
        That's why we should return 1.
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 8, 12)):
            self.cooking_exercise_group_1.limit = 1
            self.cooking_exercise_group_2.limit = 1
            engine.enqueue_student(self.bolek, self.cooking_exercise_group_1)
            engine.enqueue_student(self.lolek, self.cooking_exercise_group_2)
            engine.enqueue_student(self.tola, self.cooking_exercise_group_1)
            engine.enqueue_student(self.tola, self.cooking_exercise_group_2)
            engine.enqueue_student(self.bolek, self.cooking_exercise_group_2)
            engine.enqueue_student(self.lolek, self.cooking_exercise_group_1)

            expected_waiting = {
                self.cooking_exercise_group_1.course_id: {
                    self.cooking_exercise_group_1.type: 1,
                }
            }
            self.assertDictEqual(
                engine.list_waiting_students([self.cooking_exercise_group_1.course]),
                expected_waiting)

    def test_student_exceeds_the_final_limit(self):
        """Tests the Final ECTS limit constraint.

        Bolek will try to sign up to "Gotowanie", "Sprzątanie" and "Szydełkowanie" in this order.
        He should be successful with "Gotowanie"(35 ects) and "Szydełkowanie"(5 ects)
        He shoudn't be signed to "Sprzątanie"(11ects) due to final ects limit(45 ects).
        """
        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 4, 12)):
            self.assertTrue(engine.enqueue_student(self.bolek, self.cooking_exercise_group_1))
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        self.assertEqual(
            engine.student_points_in_semester(self.bolek, self.semester), 35)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 4, 12, 5)):
            # He shouldn't be able to join the queue.
            self.assertFalse(engine.enqueue_student(self.bolek, self.cleaning_lecture_group))
        # His enrollment with "Gotowanie" should still exist.
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.cooking_exercise_group_1,
                status=RecordStatus.ENROLLED).exists())
        # His record with "Sprzątanie" shouldn't exist.
        self.assertFalse(
            Record.objects.filter(
                student=self.bolek, group=self.cleaning_lecture_group).exists())
        self.assertEqual(
            engine.student_points_in_semester(self.bolek, self.semester), 35)

        with patch(RECORDS_DATETIME, mock_datetime(2011, 10, 4, 12, 5)):
            # He should be able to join the queue.
            self.assertTrue(engine.enqueue_student(self.bolek, self.knitting_lecture_group))
        self.assertTrue(
            Record.objects.filter(
                student=self.bolek, group=self.knitting_lecture_group,
                status=RecordStatus.ENROLLED).exists())
        self.assertEqual(
            engine.student_points_in_semester(self.bolek, self.semester), 40)

    def test_queries_num(self):
        """Tests num of queries in can_enqueue_groups.

        Num of queries should be independent of the number of groups
        """
        with self.assertNumQueries(4):
            self.assertTrue(engine.can_enqueue_groups(self.bolek, [
                self.cooking_exercise_group_1,
                self.cleaning_lecture_group,
                self.cleaning_exercise_group_1,
                self.cleaning_lecture_group,
                self.washing_up_seminar_1,
                self.cooking_exercise_group_2,
                self.cleaning_exercise_group_2,
                self.washing_up_seminar_2,
                ]))

        with self.assertNumQueries(4):
            self.assertTrue(engine.can_enqueue_groups(self.bolek, [
                self.cooking_exercise_group_1,
                self.cleaning_lecture_group,
                self.cleaning_exercise_group_1,
                ]))

        with self.assertNumQueries(4):
            self.assertTrue(engine.can_enqueue_groups(self.bolek, [
                self.cooking_exercise_group_1,
                ]))

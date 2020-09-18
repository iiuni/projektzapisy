"""Tests for the logic of auto-enrollment groups."""
import functools
from datetime import timedelta

import freezegun
from django.test import TestCase, override_settings

from apps.enrollment.courses.tests.factories import (CourseInstanceFactory, GroupFactory, GroupType)
from apps.enrollment.records.models import (GroupOpeningTimes, Record, RecordStatus, T0Times)
from apps.users.tests.factories import StudentFactory


def enrollment_time(func):
    """Decorator freezing time at records_opening and ticking slowly.

    The operations will start a minute after enrollment is opened, and every
    time measurement will be 60 seconds after the one before.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        freeze_time = freezegun.freeze_time(self.opening_time + timedelta(minutes=1),
                                            auto_tick_seconds=60)
        method_with_frozen_time = freeze_time(func)
        output = method_with_frozen_time(self, *args, **kwargs)
        return output

    return wrapper


@override_settings(RUN_ASYNC=False)
class AutoEnrollmentGroupTest(TestCase):
    """Verify correctness of our enrollment logic implementation.

    The tests are missing one important issue — the asynchronous task queue. To
    make testing easier, the test will run all tasks synchronously (eagerly).
    """
    @classmethod
    def setUpTestData(cls):
        """Computes GroupOpeningTimes for all tests."""
        course = CourseInstanceFactory()
        cls.lecture = GroupFactory(course=course,
                                   type=GroupType.LECTURE,
                                   auto_enrollment=True,
                                   extra="w")
        cls.exercise_1 = GroupFactory(course=course, type=GroupType.EXERCISES, limit=1, extra="ćw1")
        cls.exercise_2 = GroupFactory(course=course, type=GroupType.EXERCISES, limit=1, extra="ćw2")

        cls.bolek = StudentFactory(user__username='bolek')
        cls.lolek = StudentFactory(user__username='lolek')
        cls.tola = StudentFactory(user__username='tola')
        T0Times.populate_t0(course.semester)
        GroupOpeningTimes.populate_opening_times(course.semester)

        # For convenience we will store the records opening time in a separate
        # variable. Everyone will be entitled to enroll at this time.
        cls.opening_time = course.semester.records_opening
        cls.maxDiff = None

    @enrollment_time
    def test_lecture_group_also_enrolled(self):
        """Tests automatic adding into the corresponding lecture group.

        Bolek will just enqueue into the exercises group. He should also be
        enrolled into the lecture, since it is an auto-enrollment group.
        """
        self.assertTrue(Record.enqueue_student(self.bolek, self.exercise_1))
        self.assertTrue(
            Record.objects.filter(student=self.bolek,
                                  group=self.exercise_1,
                                  status=RecordStatus.ENROLLED).exists())
        self.assertTrue(
            Record.objects.filter(student=self.bolek,
                                  group=self.lecture,
                                  status=RecordStatus.ENROLLED).exists())

    @enrollment_time
    def test_lecture_group_also_removed(self):
        """Like above Bolek will enqueue into exercise group. Then he'll leave.

        He first should be automatically pulled into the lecture group. Then he
        will unenroll from the group and he should be removed from the lecture
        group as well, as the lecture group is a auto-enrollment group.
        """
        self.assertTrue(Record.enqueue_student(self.bolek, self.exercise_1))
        self.assertTrue(
            Record.objects.filter(student=self.bolek,
                                  group=self.exercise_1,
                                  status=RecordStatus.ENROLLED).exists())
        self.assertTrue(
            Record.objects.filter(student=self.bolek,
                                  group=self.lecture,
                                  status=RecordStatus.ENROLLED).exists())

        # One cannot leave the auto-enrollment group.
        self.assertFalse(Record.remove_from_group(self.bolek, self.lecture))
        # One cannot leave the group he is not in.
        self.assertFalse(Record.remove_from_group(self.bolek, self.exercise_2))
        self.assertTrue(Record.remove_from_group(self.bolek, self.exercise_1))
        self.assertFalse(
            Record.objects.filter(student=self.bolek,
                                  group=self.exercise_1,
                                  status=RecordStatus.ENROLLED).exists())
        self.assertFalse(
            Record.objects.filter(student=self.bolek,
                                  group=self.lecture,
                                  status=RecordStatus.ENROLLED).exists())

    @enrollment_time
    def test_auto_enrollment_group_queue(self):
        """Tests that auto-enrollment queue state reflects that of a course."""
        # Bolek enrolls into one exercise group. Lolek into the other.
        self.assertTrue(Record.enqueue_student(self.bolek, self.exercise_1))
        self.assertTrue(Record.enqueue_student(self.lolek, self.exercise_2))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
            ])
        # Tola enqueues into the first group. She should also be in the queue
        # for the lecture group even though there is space there.
        self.assertTrue(Record.enqueue_student(self.tola, self.exercise_1))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'tola',
                    'status': RecordStatus.QUEUED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'tola',
                    'status': RecordStatus.QUEUED
                },
            ])
        # Bolek enqueues into the second group. He is still enrolled into the
        # first, so he should be in the lecture group.
        self.assertTrue(Record.enqueue_student(self.bolek, self.exercise_2))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'tola',
                    'status': RecordStatus.QUEUED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'tola',
                    'status': RecordStatus.QUEUED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.QUEUED
                },
            ])
        # Lolek leaves the second group. Bolek should pop into his spot, leaving
        # place for Tola in the first group.
        self.assertTrue(Record.remove_from_group(self.lolek, self.exercise_2))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.REMOVED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.REMOVED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.REMOVED
                },
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'tola',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'tola',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
            ])

    @enrollment_time
    def test_transition_enrolled_to_enqueued(self):
        """Tests that auto-enrollment catches transition from enrolled to queued."""
        # Bolek enrolls into one exercise group. Lolek into the other.
        self.assertTrue(Record.enqueue_student(self.bolek, self.exercise_1))
        self.assertTrue(Record.enqueue_student(self.lolek, self.exercise_2))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
            ])
        # Lolek prefers the first group to the second.
        self.assertTrue(Record.enqueue_student(self.lolek, self.exercise_1))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.QUEUED
                },
            ])
        # Finally Lolek leaves his group and becomes unenrolled - but still
        # in the queue.
        self.assertTrue(Record.remove_from_group(self.lolek, self.exercise_2))
        self.assertCountEqual(
            Record.objects.all().values('group__extra', 'student__user__username', 'status'), [
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'ćw2',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.REMOVED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'bolek',
                    'status': RecordStatus.ENROLLED
                },
                {
                    'group__extra': 'w',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.QUEUED
                },
                {
                    'group__extra': 'ćw1',
                    'student__user__username': 'lolek',
                    'status': RecordStatus.QUEUED
                },
            ])

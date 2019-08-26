"""Tests that enrollment and queues work with guaranteed spots."""
from datetime import timedelta

from django.contrib.auth.models import Group as AuthGroup
from django.test import TestCase, override_settings
from freezegun import freeze_time

from apps.enrollment.courses.models.group import GuaranteedSpots
from apps.enrollment.courses.tests.factories import GroupFactory
from apps.enrollment.records.models import Record, T0Times
from apps.users.tests.factories import StudentFactory


@override_settings(RUN_ASYNC=False)
class GuaranteedSpotsEnrollmentTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = GroupFactory(limit=2)

        cls.bolek = StudentFactory()
        cls.lolek = StudentFactory()
        cls.tola = StudentFactory()
        cls.reksio = StudentFactory()
        cls.uszatek = StudentFactory()

        T0Times.populate_t0(cls.group.course.semester)

        # Tola and Uszatek are going to belong to the ISIM group.
        cls.isim_role = AuthGroup.objects.create(name='isim')
        cls.tola.user.groups.add(cls.isim_role)
        cls.uszatek.user.groups.add(cls.isim_role)

        GuaranteedSpots.objects.create(group=cls.group, role=cls.isim_role, limit=1)

        # For convenience we will store the records opening time in a separate
        # variable. Everyone will be entitled to enroll at this time.
        cls.opening_time = cls.group.course.semester.records_opening

    def test_isim_not_involved(self):
        """When ISIM students are not involved, enrollment behaves normally."""
        with freeze_time(self.opening_time + timedelta(seconds=5)):
            Record.enqueue_student(self.bolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=10)):
            Record.enqueue_student(self.lolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=15)):
            Record.enqueue_student(self.reksio, self.group)

        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.lolek, self.group))
        self.assertFalse(Record.is_enrolled(self.reksio, self.group))
        self.assertTrue(Record.is_recorded(self.reksio, self.group))

        with freeze_time(self.opening_time + timedelta(minutes=5)):
            Record.remove_from_group(self.lolek, self.group)

        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.reksio, self.group))
        self.assertFalse(Record.is_recorded(self.lolek, self.group))

    def test_one_isim_student(self):
        """When one ISIM student comes, he can take the guaranteed place."""
        with freeze_time(self.opening_time + timedelta(seconds=5)):
            Record.enqueue_student(self.bolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=10)):
            Record.enqueue_student(self.lolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=15)):
            Record.enqueue_student(self.reksio, self.group)

        # At this point one guy (Reksio) is in the queue.
        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.lolek, self.group))
        self.assertFalse(Record.is_enrolled(self.reksio, self.group))
        self.assertTrue(Record.is_recorded(self.reksio, self.group))

        with freeze_time(self.opening_time + timedelta(minutes=1)):
            Record.enqueue_student(self.tola, self.group)

        # Reksio is still waiting, but Tola took the ISIM guaranteed spot.
        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.lolek, self.group))
        self.assertFalse(Record.is_enrolled(self.reksio, self.group))
        self.assertTrue(Record.is_recorded(self.reksio, self.group))
        self.assertTrue(Record.is_enrolled(self.tola, self.group))

        with freeze_time(self.opening_time + timedelta(minutes=5)):
            Record.remove_from_group(self.lolek, self.group)

        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.reksio, self.group))
        self.assertFalse(Record.is_recorded(self.lolek, self.group))
        self.assertTrue(Record.is_enrolled(self.tola, self.group))

        with freeze_time(self.opening_time + timedelta(minutes=10)):
            Record.enqueue_student(self.lolek, self.group)

        # Now Lolek sits in the queue.
        self.assertTrue(Record.is_recorded(self.lolek, self.group))
        self.assertFalse(Record.is_enrolled(self.lolek, self.group))

        with freeze_time(self.opening_time + timedelta(minutes=15)):
            Record.remove_from_group(self.tola, self.group)

        # Now that Tola has left, the ISIM spot is free, but Lolek is still in
        # the queue.
        self.assertFalse(Record.is_recorded(self.tola, self.group))
        self.assertTrue(Record.is_recorded(self.lolek, self.group))
        self.assertFalse(Record.is_enrolled(self.lolek, self.group))

    def test_two_isim_students(self):
        """When there are two ISIM students, they compete for the regular spots
        and the guaranteed spot at the same time.
        """
        with freeze_time(self.opening_time + timedelta(seconds=5)):
            Record.enqueue_student(self.bolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=10)):
            Record.enqueue_student(self.lolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=15)):
            Record.enqueue_student(self.tola, self.group)
        # Bolek and Lolek are in the regular spots, Tola has taken the
        # ISIM-guaranteed extra spot.
        self.assertTrue(Record.is_enrolled(self.bolek, self.group))
        self.assertTrue(Record.is_enrolled(self.lolek, self.group))
        self.assertTrue(Record.is_enrolled(self.tola, self.group))

        with freeze_time(self.opening_time + timedelta(seconds=20)):
            Record.enqueue_student(self.reksio, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=25)):
            Record.enqueue_student(self.uszatek, self.group)
        # Now both Reksio and Uszatek are waiting.
        self.assertFalse(Record.is_enrolled(self.reksio, self.group))
        self.assertFalse(Record.is_enrolled(self.uszatek, self.group))

        with freeze_time(self.opening_time + timedelta(seconds=30)):
            Record.remove_from_group(self.tola, self.group)
        # Now Uszatek jumps into the guaranteed spot even though he is not first
        # in line.
        self.assertFalse(Record.is_enrolled(self.reksio, self.group))
        self.assertTrue(Record.is_enrolled(self.uszatek, self.group))

        with freeze_time(self.opening_time + timedelta(seconds=35)):
            Record.enqueue_student(self.tola, self.group)
            Record.remove_from_group(self.lolek, self.group)
        # Now Reksio takes up the regular spot. Tola is waiting.
        self.assertTrue(Record.is_enrolled(self.reksio, self.group))
        self.assertFalse(Record.is_enrolled(self.tola, self.group))

        with freeze_time(self.opening_time + timedelta(seconds=40)):
            Record.enqueue_student(self.lolek, self.group)
        with freeze_time(self.opening_time + timedelta(seconds=45)):
            Record.remove_from_group(self.bolek, self.group)
        # Now Tola assumes the regular spot, because she was in line before
        # Lolek.
        self.assertTrue(Record.is_enrolled(self.uszatek, self.group))
        self.assertTrue(Record.is_enrolled(self.tola, self.group))
        self.assertFalse(Record.is_enrolled(self.lolek, self.group))

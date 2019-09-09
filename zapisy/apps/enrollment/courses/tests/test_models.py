from datetime import datetime, timedelta, date

from django.core.validators import ValidationError
from django.test import TestCase
from zapisy import common

from apps.enrollment.courses.models.semester import Freeday, ChangedDay, Semester
from apps.enrollment.courses.tests.objectmothers import SemesterObjectMother
from apps.offer.proposal.tests.factories import ProposalFactory

from ..models import CourseInstance


class FreedayTestCase(TestCase):
    def setUp(self):
        freeday = Freeday(day=datetime(2015, 1, 1))
        freeday.save()

        freeday2 = Freeday(day=datetime(2015, 2, 3))
        freeday2.save()

        freeday3 = Freeday(day=datetime(2016, 5, 6))
        freeday3.save()

    def test_free_day_status(self):
        self.assertTrue(Freeday.is_free(datetime(2015, 1, 1)))
        self.assertFalse(Freeday.is_free(datetime(2015, 1, 2)))
        self.assertFalse(Freeday.is_free(datetime(2016, 1, 1)))
        self.assertFalse(Freeday.is_free(datetime(2022, 1, 30)))

    def test_free_day_count(self):
        freedays = Freeday.objects.all()
        self.assertEqual(len(freedays), 3)


class ChangedDayTestCase(TestCase):
    def setUp(self):
        semester = SemesterObjectMother.winter_semester_2015_16()
        semester.save()

        change1 = ChangedDay(
            day=semester.semester_beginning + timedelta(days=3),
            weekday=common.SUNDAY
        )
        change1.save()
        change2 = ChangedDay(
            day=semester.semester_beginning + timedelta(days=4),
            weekday=common.SUNDAY
        )
        change2.save()

        change3 = ChangedDay(
            day=semester.semester_beginning + timedelta(days=2),
            weekday=common.SATURDAY
        )
        change3.save()

    def test_count_added_sundays_winter_semester(self):
        semester = Semester.get_semester(datetime(2015, 11, 10))
        self.assertNotEqual(semester, None)
        changed_days = ChangedDay.get_added_days_of_week(semester.semester_beginning,
                                                         semester.semester_ending,
                                                         common.SUNDAY)

        self.assertEqual(len(changed_days), 2)

    def test_count_changed_days_in_winter_semester(self):
        semester = Semester.get_semester(datetime(2015, 11, 10))
        self.assertNotEqual(semester, None)
        changed_days = ChangedDay.get_added_days_of_week(semester.semester_beginning,
                                                         semester.semester_ending)

        self.assertEqual(len(changed_days), 3)

    def test_clean_on_changing_sunday_to_sunday(self):
        changed_day = ChangedDay(day=datetime(2016, 3, 27),
                                 weekday=common.SUNDAY)
        self.assertRaises(ValidationError, changed_day.clean)


class SemesterTestCase(TestCase):
    def setUp(self):
        semester1 = SemesterObjectMother.summer_semester_2015_16()
        semester1.save()

        semester2 = SemesterObjectMother.winter_semester_2015_16()
        semester2.save()

        friday_to_sunday = ChangedDay(
            day=date(2015, 10, 16),
            weekday=common.SUNDAY
        )
        friday_to_sunday.save()

    def test_get_correct_semester(self):
        winter_semester = Semester.get_semester(datetime(2015, 12, 25))
        self.assertEqual(winter_semester.type, Semester.TYPE_WINTER)
        summer_semester = Semester.get_semester(datetime(2016, 5, 20))
        self.assertEqual(summer_semester.type, Semester.TYPE_SUMMER)

        some_semester = Semester.get_semester(winter_semester.semester_ending + timedelta(days=1))
        self.assertEqual(some_semester.type, Semester.TYPE_SUMMER)

    def test_get_all_sundays_in_winter_semester(self):
        winter_semester = Semester.get_semester(datetime(2015, 12, 1))
        sundays = winter_semester.get_all_days_of_week(common.SUNDAY)
        self.assertTrue(sundays)
        # a sunday in winter semester
        a_sunday = date(2015, 12, 6)
        another_sunday = date(2015, 11, 22)
        self.assertTrue(a_sunday in sundays)
        self.assertTrue(another_sunday in sundays)

    def test_count_added_sundays(self):
        winter_semester = Semester.get_semester(datetime(2015, 12, 1))
        sundays_added = winter_semester.get_all_added_days_of_week(common.SUNDAY)
        self.assertTrue(sundays_added)


class CourseInstanceTestCase(TestCase):
    def test_create_course_from_proposal(self):
        """Tests creating a course instance from the proposal."""
        semester = SemesterObjectMother.winter_semester_2015_16()
        semester.save()
        proposal = ProposalFactory()

        course = CourseInstance.create_proposal_instance(proposal, semester)

        self.assertEqual(proposal.name, course.name)
        self.assertEqual(proposal.owner, course.owner)
        self.assertEqual(proposal, course.offer)
        self.assertEqual(semester, course.semester)
        self.assertNotEqual(proposal.id, course.id)
        self.assertNotEqual(proposal.created, course.created)

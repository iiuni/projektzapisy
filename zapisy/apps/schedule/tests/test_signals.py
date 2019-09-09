from datetime import date, time

from django import test

from apps.enrollment.courses.tests.factories import (CourseInstanceFactory, GroupFactory,
                                                     SemesterFactory, ClassroomFactory)
from apps.enrollment.courses.models.semester import ChangedDay, Freeday
from apps.enrollment.courses.models.term import Term as CourseTerm
from apps.schedule.models.term import Term
from zapisy import common


class TermModificationsOnSignalTest(test.TestCase):
    """Tests automatically triggered modifications to schedule terms.

    Terms in this application are created and modified automatically upon
    modifications to courses.Term objects. This logic is quite complicated.
    """

    @classmethod
    def setUpTestData(cls):
        # Our semester is only going to take place in May 2019.
        cls.semester = SemesterFactory(lectures_beginning=date(2019, 5, 1),
                                       lectures_ending=date(2019, 5, 31))
        # We change one Thursday to Friday and one Friday to Thursday.
        ChangedDay.objects.create(day=date(2019, 5, 16), weekday=common.FRIDAY)
        ChangedDay.objects.create(day=date(2019, 5, 17), weekday=common.THURSDAY)
        # One Thursday is going to be free.
        Freeday.objects.create(day=date(2019, 5, 9))

        # There is going to be one course only.
        course = CourseInstanceFactory(semester=cls.semester)
        cls.group = GroupFactory(course=course)

        cls.classrooms = [ClassroomFactory(), ClassroomFactory()]

    def test_thursday_terms_added(self):
        """A simple scenario where we just add a term."""
        t = CourseTerm.objects.create(group=self.group,
                                      dayOfWeek=common.THURSDAY,
                                      start_time=time(12),
                                      end_time=time(14))
        t.classrooms.add(self.classrooms[0])

        self.assertCountEqual(Term.objects.all().values_list('day', flat=True), [
            date(2019, 5, 2),
            date(2019, 5, 17),
            date(2019, 5, 23),
            date(2019, 5, 30),
        ])

        # Now let's move it two hours earlier.
        t.start_time = time(10)
        t.end_time = time(12)
        t.save()
        self.assertCountEqual(Term.objects.all().values_list('day', 'start', 'end'), [
            (date(2019, 5, 2), time(10), time(12)),
            (date(2019, 5, 17), time(10), time(12)),
            (date(2019, 5, 23), time(10), time(12)),
            (date(2019, 5, 30), time(10), time(12)),
        ])

    def test_switch_date_and_classroom(self):
        """We move the class to different time and classroom."""
        # This is the same as above.
        t = CourseTerm.objects.create(group=self.group,
                                      dayOfWeek=common.THURSDAY,
                                      start_time=time(12),
                                      end_time=time(14))
        t.classrooms.add(self.classrooms[0])
        # Now we move the class to the other time.
        t.dayOfWeek = common.FRIDAY
        t.save()
        self.assertCountEqual(Term.objects.all().values_list('day', flat=True), [
            date(2019, 5, 3),
            date(2019, 5, 10),
            date(2019, 5, 16),
            date(2019, 5, 24),
            date(2019, 5, 31),
        ])
        # And move it to a different room.
        t.classrooms.set(self.classrooms[1:])
        self.assertCountEqual(Term.objects.all().values_list('day', flat=True), [
            date(2019, 5, 3),
            date(2019, 5, 10),
            date(2019, 5, 16),
            date(2019, 5, 24),
            date(2019, 5, 31),
        ])
        self.assertFalse(Term.objects.filter(room=self.classrooms[0]).exists())
        self.assertEqual(Term.objects.filter(room=self.classrooms[1]).count(), 5)

    def test_class_with_many_terms(self):
        # We create one term just as before
        t1 = CourseTerm.objects.create(group=self.group,
                                       dayOfWeek=common.THURSDAY,
                                       start_time=time(12),
                                       end_time=time(14))
        t1.classrooms.add(self.classrooms[0])
        # And we add another.
        t2 = CourseTerm.objects.create(group=self.group,
                                       dayOfWeek=common.WEDNESDAY,
                                       start_time=time(10),
                                       end_time=time(12))
        t2.classrooms.add(self.classrooms[1])

        self.assertCountEqual(Term.objects.all().values_list('day', 'room_id'), [
            (date(2019, 5, 1), self.classrooms[1].pk),
            (date(2019, 5, 8), self.classrooms[1].pk),
            (date(2019, 5, 15), self.classrooms[1].pk),
            (date(2019, 5, 22), self.classrooms[1].pk),
            (date(2019, 5, 29), self.classrooms[1].pk),
            (date(2019, 5, 2), self.classrooms[0].pk),
            (date(2019, 5, 17), self.classrooms[0].pk),
            (date(2019, 5, 23), self.classrooms[0].pk),
            (date(2019, 5, 30), self.classrooms[0].pk),
        ])

        # Now we move the Thursday term to Friday.
        t1.dayOfWeek = common.FRIDAY
        t1.save()
        self.assertCountEqual(Term.objects.all().values_list('day', 'room_id'), [
            (date(2019, 5, 1), self.classrooms[1].pk),
            (date(2019, 5, 8), self.classrooms[1].pk),
            (date(2019, 5, 15), self.classrooms[1].pk),
            (date(2019, 5, 22), self.classrooms[1].pk),
            (date(2019, 5, 29), self.classrooms[1].pk),
            (date(2019, 5, 3), self.classrooms[0].pk),
            (date(2019, 5, 10), self.classrooms[0].pk),
            (date(2019, 5, 16), self.classrooms[0].pk),
            (date(2019, 5, 24), self.classrooms[0].pk),
            (date(2019, 5, 31), self.classrooms[0].pk),
        ])
        # And we give it two classrooms.
        t1.classrooms.set(self.classrooms)
        self.assertCountEqual(Term.objects.all().values_list('day', 'room_id'), [
            (date(2019, 5, 1), self.classrooms[1].pk),
            (date(2019, 5, 8), self.classrooms[1].pk),
            (date(2019, 5, 15), self.classrooms[1].pk),
            (date(2019, 5, 22), self.classrooms[1].pk),
            (date(2019, 5, 29), self.classrooms[1].pk),
            (date(2019, 5, 3), self.classrooms[0].pk),
            (date(2019, 5, 10), self.classrooms[0].pk),
            (date(2019, 5, 16), self.classrooms[0].pk),
            (date(2019, 5, 24), self.classrooms[0].pk),
            (date(2019, 5, 31), self.classrooms[0].pk),
            (date(2019, 5, 3), self.classrooms[1].pk),
            (date(2019, 5, 10), self.classrooms[1].pk),
            (date(2019, 5, 16), self.classrooms[1].pk),
            (date(2019, 5, 24), self.classrooms[1].pk),
            (date(2019, 5, 31), self.classrooms[1].pk),
        ])

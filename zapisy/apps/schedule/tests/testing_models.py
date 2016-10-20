# -*- coding: utf-8 -*-
from django.test import TestCase
from zapisy.apps.schedule.models import SpecialReservation, Event, Term as EventTerm
from apps.enrollment.courses.models import Semester, Classroom, Term
from datetime import datetime, timedelta, time, date
from django.core.serializers import serialize
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from apps.enrollment.courses.tests.objectmothers import SemesterObjectMother, ClassroomObjectMother
from apps.users.tests.objectmothers import UserObjectMother

import zapisy.common as common

class SpecialReservationTestCase(TestCase):

    def setUp(self):
        semester = SemesterObjectMother.summer_semester_2015_16()
        semester.save()

        semester_2 = SemesterObjectMother.winter_semester_2015_16()
        semester_2.save()

        room110 = ClassroomObjectMother.room110()
        room110.save()

        room104 = ClassroomObjectMother.room104()
        room104.save()

        reservation = SpecialReservation(semester=semester,
                                         title="A reservation",
                                         classroom=room110,
                                         dayOfWeek=common.WEDNESDAY,
                                         start_time=time(15),
                                         end_time=time(16))
        reservation.full_clean()
        reservation.save()

        reservation_2 = SpecialReservation(semester=semester,
                                          title=u'ąęłżóćśśń',
                                          classroom=room110,
                                          dayOfWeek=common.THURSDAY,
                                          start_time=time(15),
                                          end_time=time(16))
        reservation_2.full_clean()
        reservation_2.save()

        reservation_3 = SpecialReservation(semester=semester_2,
                                           title='Reserve whole monday',
                                           classroom=room110,
                                           dayOfWeek=common.MONDAY,
                                           start_time=time(8),
                                           end_time=time(21))
        reservation_3.full_clean()
        reservation_3.save()

    def test_created_reservation_is_present(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertTrue(reservations)

    def test_no_reservations_on_not_reserved_day(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester, day=common.FRIDAY)
        self.assertFalse(reservations)

    def test_number_of_reservations(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertEqual(len(reservations), 2)
        
    def test_try_clean_on_non_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='non-overlapping reservation',
            classroom=room,
            dayOfWeek=common.THURSDAY,
            start_time=time(14),
            end_time=time(15)
        )
        reservation.full_clean()

    def test_find_child_events(self):
        events = Event.objects.all()
        self.assertTrue(events)

    def test_special_reservation_unicode_method(self):
        reservations = SpecialReservation.objects.all()
        for reservation in reservations:
            unicode(reservation)


class EventTestCase(TestCase):

    def setUp(self):
        teacher = UserObjectMother.user_jan_kowalski()
        teacher.save()
        profile = UserObjectMother.teacher_profile(teacher)
        profile.save()
        employee = UserObjectMother.employee(teacher)
        employee.save()

        room110 = ClassroomObjectMother.room110()
        room110.save()

        teacher = User.objects.all()[0]
        event = Event(
            title='an event',
            description='an event',
            type=Event.TYPE_GENERIC,
            status=Event.STATUS_ACCEPTED,
            author=teacher,
        )
        event.full_clean()
        event.save()

        room110 = Classroom.get_by_number('110')
        event = Event.objects.all()[0]

        term_1 = EventTerm(
            event=event,
            day=date(2016, 5, 20),
            start=time(15),
            end=time(16),
            room=room110
        )
        term_1.full_clean()
        term_1.save()

        term_2 = EventTerm(
            event=event,
            day=term_1.day,
            start=time(16),
            end=time(17),
            room=room110
        )
        term_2.full_clean()
        term_2.save()

    def test_event_is_present(self):
        room = Classroom.get_by_number('110')
        terms = EventTerm.get_terms_for_dates(dates=[date(2016, 5, 20)],
                                              classroom=room)
        self.assertTrue(terms)

    def test_clean_overlapping_term(self):
        event = Event.objects.all()[0]
        room110 = Classroom.get_by_number('110')
        term = EventTerm(
            event=event,
            day=date(2016, 5, 20),
            start=time(15),
            end=time(17),
            room=room110
        )
        self.assertRaises(ValidationError, term.full_clean)

    def test_remove_event_and_terms(self):
        event = Event.objects.all()[0]
        event.delete()
        terms = EventTerm.objects.all()
        self.assertFalse(terms)

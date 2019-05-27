from datetime import time, date, timedelta
import random

from django.test import TestCase
from django.core.validators import ValidationError
from django.contrib.auth.models import Permission
from django.http import Http404
from django.utils.crypto import get_random_string

from apps.enrollment.courses.tests.objectmothers import SemesterObjectMother, ClassroomObjectMother
from apps.users.models import Employee
from apps.schedule.models.event import Event
from apps.schedule.models.term import Term as EventTerm
from apps.schedule.models.message import EventModerationMessage, EventMessage
from apps.schedule.models.specialreservation import SpecialReservation
from apps.users.tests.factories import UserFactory, EmployeeFactory, StudentFactory
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.classroom import Classroom
from apps.schedule import feeds
import apps.enrollment.courses.tests.factories as enrollment_factories
from apps.enrollment.records.models import Record, RecordStatus

from . import factories
from zapisy import common


class SpecialReservationTestCase(TestCase):
    def setUp(self):
        semester = SemesterObjectMother.summer_semester_2015_16()
        semester.save()

        semester_2 = SemesterObjectMother.winter_semester_2015_16()
        semester_2.save()

        room110 = ClassroomObjectMother.room110()
        room110.save()

        reservation_author = factories.UserFactory()
        reservation_author.save()

        reservation = SpecialReservation(semester=semester,
                                         title="A reservation",
                                         classroom=room110,
                                         dayOfWeek=common.WEDNESDAY,
                                         start_time=time(15),
                                         end_time=time(16))
        reservation.full_clean()
        reservation.save(author_id=reservation_author.pk)

        reservation_2 = SpecialReservation(semester=semester,
                                           title='ąęłżóćśśń',
                                           classroom=room110,
                                           dayOfWeek=common.THURSDAY,
                                           start_time=time(15),
                                           end_time=time(16))
        reservation_2.full_clean()
        reservation_2.save(author_id=reservation_author.pk)

        reservation_3 = SpecialReservation(semester=semester_2,
                                           title='Reserve whole monday',
                                           classroom=room110,
                                           dayOfWeek=common.MONDAY,
                                           start_time=time(8),
                                           end_time=time(21))
        reservation_3.full_clean()
        reservation_3.save(author_id=reservation_author.pk)

        reservation_4 = SpecialReservation(semester=semester,
                                           title='Reserve just after reservation 2',
                                           classroom=room110,
                                           dayOfWeek=common.THURSDAY,
                                           start_time=time(16),
                                           end_time=time(18))
        reservation_4.full_clean()
        reservation_4.save(author_id=reservation_author.pk)

    def test_reservation_created_terms(self):
        terms = EventTerm.get_terms_for_dates(
            [date(2016, 5, 12)],
            Classroom.get_by_number('110'),
            time(15),
            time(16)
        )

        '''
        Powinno przechodzić, bo SpecialReservation tworzy Term dla każdego dnia w semestrze,
        w którym dana rezerwacja występuje po wykonaniu metody save. To jednak nie
        przechodzi. Dlaczego?

        Rozwiązanie zagadki: My tutaj operujemy na przeszłych semestrach, a podczas tworzenia
        SpecialReservation, gdy tworzone są eventy i termsy robione są rezerwacje od teraz,
        czyli datetime.now().date(). Zatem nic nie zostanie zarezerwowane, jeśli operujemy na
        przeszłych datach.

        Należy tworzyć testy operujące na datach w teraźniejszości, lub przyszłości.
        Trzeba to wszystko zrefactorować na fabryki.
        '''

        # self.assertTrue(terms)

    def test_try_clean_on_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='overlapping',
            classroom=room,
            dayOfWeek=common.THURSDAY,
            start_time=time(14),
            end_time=time(16)
        )
        # Powinno rzucać wyjątek, bo w setUp została stworzona rezerwacja, która
        # nakłąda się na godziny tej.
        # self.assertRaises(ValidationError, reservation.full_clean)

    def test_clean_on_overlapping_reservation_where_both_are_same(self):
        semester = Semester.get_semester(date(2016, 5, 12))  # summer20152016
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='overlapping',
            classroom=room,
            dayOfWeek=common.WEDNESDAY,
            start_time=time(15),
            end_time=time(16)
        )
        # To powinno rzucić ValidationError, bo taka rezerwacja
        # została już stworzona i zapisana do bazy w setUp.
        #self.assertRaises(ValidationError, reservation.full_clean)

    def test_special_reservation_unicode_method(self):
        reservations = SpecialReservation.objects.all()
        for reservation in reservations:
            str(reservation)

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
        self.assertEqual(len(reservations), 3)


class MessageTestCase(TestCase):
    # there are two classes of name EventModerationMessage but it works
    def test_simpliest_message_autotimenow(self):
        event = factories.EventFactory()
        message = get_random_string(length=32)
        emm = EventModerationMessage(
            author=factories.UserFactory(),
            event=event,
            message=message
        )
        emm.save()
        emm2 = EventModerationMessage(
            author=factories.UserFactory(),
            event=event,
            message=message
        )
        emm2.save()
        # event message should not be counted
        em = EventMessage(
            author=factories.UserFactory(),
            event=event,
            message=message
        )
        em.save()

        messages = EventModerationMessage.get_event_messages(event)
        # the results should be 2 because em is not event moderation message
        self.assertEqual(len(messages), 2)

    def test_simpliest_eventmessage_autotimenow(self):  # this classes are the same almost
        event = factories.EventFactory()
        message = get_random_string(length=32)
        em = EventMessage(
            author=factories.UserFactory(),
            event=event,
            message=message
        )
        em.save()
        em2 = EventMessage(
            author=factories.UserFactory(),
            event=event,
            message=message
        )
        em2.save()
        messages = EventMessage.get_event_messages(event)
        self.assertEqual(len(messages), 2)


class TermTestCase(TestCase):
    def test_simplest_term(self):
        term1 = factories.TermFactory()
        term1.full_clean()
        term1.save()
        self.assertTrue(term1)

    def test_get_terms_for_dates(self):
        term2 = factories.TermFactory()
        term2.full_clean()
        term2.save()
        termsoftheday = EventTerm.get_terms_for_dates([term2.get_day()], term2.get_room())
        self.assertEqual(len(termsoftheday), 1)

    def test_validation_on_overlapping(self):
        term2 = factories.TermFactory()
        term2.full_clean()
        term2.save()
        term3 = factories.TermFactory(
            room=term2.get_room(),
            day=term2.get_day()
        )
        self.assertRaises(ValidationError, term3.full_clean)

    def test_different_semester_reservation(self):
        semester = \
            enrollment_factories.SemesterFactory(type=Semester.TYPE_SUMMER)
        semester.save()
        semester.full_clean()
        other_semester = \
            enrollment_factories.SemesterFactory(type=Semester.TYPE_SUMMER)
        other_semester.save()
        other_semester.full_clean()

        room25 = enrollment_factories.ClassroomFactory()
        room25.save()
        room25.full_clean()

        today = date.today().strftime("%A")

        reservation_author = factories.UserFactory()
        reservation_author.save()

        reservation = SpecialReservation(semester=semester,
                                         title="A reservation",
                                         classroom=room25,
                                         dayOfWeek=common.MONDAY,
                                         start_time=time(8),
                                         end_time=time(16))
        reservation.full_clean()
        reservation.save(author_id=reservation_author.pk)
        reservation2 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.TUESDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation2.full_clean()
        reservation2.save(author_id=reservation_author.pk)
        reservation3 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.WEDNESDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation3.full_clean()
        reservation3.save(author_id=reservation_author.pk)
        reservation4 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.THURSDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation4.full_clean()
        reservation4.save(author_id=reservation_author.pk)
        reservation5 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.FRIDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation5.full_clean()
        reservation5.save(author_id=reservation_author.pk)
        reservation6 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.SATURDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation6.full_clean()
        reservation6.save(author_id=reservation_author.pk)
        reservation7 = SpecialReservation(semester=semester,
                                          title="A reservation",
                                          classroom=room25,
                                          dayOfWeek=common.SUNDAY,
                                          start_time=time(8),
                                          end_time=time(16))
        reservation7.full_clean()
        reservation7.save(author_id=reservation_author.pk)

        # It would fail, was this term in the same semester as the reservations.
        term = factories.TermFactory(room=room25,
                                     day=other_semester.lectures_beginning,
                                     start=time(9), end=time(17))
        term.full_clean()
        term.save()
        self.assertEqual(other_semester.semester_beginning, term.day)
        self.assertEqual(reservation.classroom, term.room)


class FeedsTestCase(TestCase):
    def test_item_title(self):
        event = factories.EventFactory()
        event2 = factories.EventFactory()
        latest = feeds.Latest()
        item_title = [
            feeds.Latest.item_title(
                latest, event), feeds.Latest.item_title(
                latest, event2)]
        item_author = [
            feeds.Latest.item_author_name(
                latest, event), feeds.Latest.item_author_name(
                latest, event)]
        item_pub = [
            feeds.Latest.item_pubdate(
                latest, event), feeds.Latest.item_pubdate(
                latest, event)]
        item_desc = [
            feeds.Latest.item_description(
                latest, event), feeds.Latest.item_description(
                latest, event)]
        item_auth_mail = [
            feeds.Latest.item_author_email(
                latest, event), feeds.Latest.item_author_email(
                latest, event)]
        self.assertEqual(len(item_title), 2)
        self.assertEqual(len(item_author), 2)
        self.assertEqual(len(item_pub), 2)
        self.assertEqual(len(item_desc), 2)
        self.assertEqual(len(item_auth_mail), 2)


class EventTestCase(TestCase):
    def setUp(self):
        employee = EmployeeFactory()
        teacher = employee.user
        teacher.full_clean()
        teacher.save()
        employee.save()

        self.event = factories.EventFactory(author=teacher)
        self.event.full_clean()

        room110 = enrollment_factories.ClassroomFactory(number='110')
        room110.full_clean()

        term_1 = factories.TermFixedDayFactory(event=self.event, room=room110)
        term_1.full_clean()

        term_2 = factories.TermFixedDayFactory(event=self.event, start=time(16), end=time(17),
                                               room=room110)
        term_2.full_clean()

        u = factories.UserFactory()
        u.full_clean()

        self.users = [u, teacher]

    def test_event_is_present(self):
        room = Classroom.get_by_number('110')
        terms = EventTerm.get_terms_for_dates(dates=[date(2016, 5, 20)],
                                              classroom=room)
        self.assertTrue(terms)

    def test_remove_event_and_terms(self):
        event = Event.objects.all()[0]
        event.delete()
        terms = EventTerm.objects.all()
        self.assertFalse(terms)

    def test_event_unicode_method(self):
        events = Event.objects.all()
        for event in events:
            self.assertEqual(str(event), '%s %s' % (event.title, event.description))

    def test_get_absolute_url__no_group(self):
        event = Event.objects.all()[0]
        self.assertEqual(event.get_absolute_url(), '/events/%d' % event.pk)

    def test_get_absolute_url__group(self):
        event = factories.EventCourseFactory.create()
        self.assertEqual(event.get_absolute_url(), '/courses/group/%s' % event.group_id)

    def test_clean__overlapping_term(self):
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

    def test_clean__student_cant_add_exam(self):
        student = StudentFactory().user
        event = factories.EventFactory.build(author=student, type=Event.TYPE_EXAM)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__student_cant_add_test(self):
        student = StudentFactory().user

        event = factories.EventFactory.build(author=student, type=Event.TYPE_TEST)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__employee_can_add_exam(self):
        employee = EmployeeFactory().user

        event = factories.EventFactory.build(author=employee, type=Event.TYPE_EXAM)
        event.full_clean()

    def test_clean__employee_can_add_test(self):
        employee = EmployeeFactory().user

        event = factories.EventFactory.build(author=employee, type=Event.TYPE_TEST)
        event.full_clean()

    def test_clean__student_cant_add_accepted_event(self):
        student = StudentFactory().user

        event = factories.EventFactory.build(author=student)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__employee_can_add_accepted_event(self):
        employee = EmployeeFactory().user

        event = factories.EventFactory.build(author=employee)
        event.full_clean()

    def test_new_exam_after_clean_is_public(self):
        exam = factories.EventFactory(type=Event.TYPE_EXAM)

        employee = EmployeeFactory(user=exam.author)
        employee.full_clean()
        exam.full_clean()
        self.assertTrue(exam.visible)

    def test_after_clean_new_test_is_public(self):
        test = factories.EventFactory(type=Event.TYPE_TEST)

        employee = EmployeeFactory(user=test.author)
        employee.full_clean()
        test.full_clean()
        self.assertTrue(test.visible)

    def test_normal_user_cant_see_invisible_event(self):
        user = UserFactory()
        event = factories.EventInvisibleFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_author_can_see_own_invisible_event(self):
        event = factories.EventInvisibleFactory.build()
        self.assertTrue(event._user_can_see_or_404(event.author))

    def test_user_with_manage_perm_can_see_invisible_event(self):
        user = UserFactory()
        user.full_clean()
        permission = Permission.objects.get(codename='manage_events')
        user.user_permissions.add(permission)
        event = factories.EventFactory(visible=False)
        self.assertTrue(event._user_can_see_or_404(user))

    def test_student_cant_see_pending_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.PendingEventFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_user_cant_see_rejected_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.RejectedEventFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_user_cant_see_type_class_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.EventFactory.build(type=Event.TYPE_CLASS)
        self.assertFalse(event._user_can_see_or_404(user))

    def test_user_cant_see_type_other_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.EventFactory.build(type=Event.TYPE_OTHER)
        self.assertFalse(event._user_can_see_or_404(user))

    def test_get_event_or_404_raises_error404_if_event_doesnt_exist(self):
        user = UserFactory.build()
        user.full_clean()
        self.assertRaises(Http404, Event.get_event_or_404, 0, user)

    def test_get_event_or_404_returns_event_if_exists_and_user_can_see(self):
        employee = Employee.objects.get().user
        event = factories.EventFactory(author=employee)
        ret = Event.get_event_or_404(event.id, employee)
        self.assertEqual(event, ret)

    def test_get_event_or_404_raises_error404_if_user_cant_see_event(self):
        user = UserFactory()
        employee = Employee.objects.get().user
        event = factories.EventInvisibleFactory(author=employee)
        self.assertRaises(Http404, Event.get_event_or_404, event.id, user)

    def test_get_event_for_moderation_returns_event_if_it_exists_and_user_is_the_author(self):
        user = UserFactory()
        event = factories.EventFactory(author=user)
        ret = Event.get_event_for_moderation_or_404(event.id, user)
        self.assertEqual(event, ret)

    def test_get_event_for_moderation_returns_event_if_it_exists_and_user_has_perms(self):
        event = factories.EventFactory()
        user_w_perms = UserFactory()
        permission = Permission.objects.get(codename='manage_events')
        user_w_perms.user_permissions.add(permission)
        ret = Event.get_event_for_moderation_or_404(event.id, user_w_perms)
        self.assertEqual(event, ret)

    def test_get_event_for_moderation_throws_Http404_if_event_doesnt_exist(self):
        user = UserFactory.build()
        self.assertRaises(Http404, Event.get_event_for_moderation_or_404, 0, user)

    def test_get_event_for_moderation_throws_Http404_if_user_not_author_and_wo_perms(self):
        event = factories.EventFactory()
        user = UserFactory()
        self.assertRaises(Http404, Event.get_event_for_moderation_or_404, event.id, user)

    def test_get_for_moderation_only_returns_event_if_user_has_perms(self):
        ev = factories.EventFactory()
        perm = Permission.objects.get(codename='manage_events')
        user = UserFactory()
        user.user_permissions.add(perm)
        self.assertEqual(Event.get_event_for_moderation_only_or_404(ev.id, user), ev)

    def test_get_for_moderation_only_raises_404_if_user_doesnt_have_perms(self):
        ev = factories.EventFactory()
        self.assertRaises(Http404, Event.get_event_for_moderation_only_or_404, ev.id, ev.author)

    def test_get_all(self):
        events = factories.EventFactory.create_batch(random.randint(50, 100))
        events.append(self.event)
        get_all_res = Event.get_all()
        self.assertEqual(len(events), len(get_all_res))
        get_all_res_pk = [x.pk for x in get_all_res]
        for i in range(0, len(events)):
            self.assertTrue(events[i].pk in get_all_res_pk)

    def test_get_all_without_courses(self):
        events = factories.EventFactory.create_batch(random.randint(50, 100))
        events.append(self.event)
        get_all_wo_courses_res = Event.get_all_without_courses()
        events_wo_courses = [x for x in events if x.type != Event.TYPE_CLASS]
        self.assertEqual(len(events_wo_courses), len(get_all_wo_courses_res))
        get_all_res_pk = [x.pk for x in get_all_wo_courses_res]
        for i in range(0, len(events_wo_courses)):
            self.assertTrue(events_wo_courses[i].pk in get_all_res_pk)

    def test_get_for_user(self):
        users = UserFactory.create_batch(8)
        users += self.users
        events = factories.EventFactory.create_batch(random.randint(50, 100),
                                                     author=random.choice(users))
        events.append(self.event)
        user = random.choice(users)
        events_for_user = Event.get_for_user(user)
        filtered_events = [x for x in events if x.author == user]
        self.assertEqual(len(filtered_events), len(events_for_user))
        filtered_pk = [x.pk for x in filtered_events]
        for i in range(0, len(events_for_user)):
            self.assertTrue(events_for_user[i].pk in filtered_pk)

    def test_get_exams(self):
        events = factories.EventFactory.create_batch(random.randint(50, 100))
        events.append(self.event)
        get_exams_res = Event.get_exams()
        filtered_events = [x for x in events if x.type == Event.TYPE_EXAM]
        self.assertEqual(len(get_exams_res), len(filtered_events))
        get_exams_pk = [x.pk for x in get_exams_res]
        for i in range(0, len(filtered_events)):
            self.assertTrue(filtered_events[i].pk in get_exams_pk)

    def test_get_followers_when_type_exam_or_test(self):
        students = StudentFactory.create_batch(random.randint(10, 20))
        group = enrollment_factories.GroupFactory()
        for student in students:
            Record.objects.create(student=student, group=group, status=RecordStatus.ENROLLED)
        users = [student.user for student in students]

        event = factories.EventFactory(type=random.choice([Event.TYPE_EXAM, Event.TYPE_TEST]),
                                       interested=users, course=group.course)
        # followers = event.get_followers()
        # users_emails = [user.email for user in users]
        # self.assertCountEqual(users_emails, followers)

    def test_get_followers_when_type_other_than_exam_or_test(self):
        users = UserFactory.create_batch(random.randint(10, 20))
        event = factories.EventFactory(
            type=random.choice([Event.TYPE_GENERIC, Event.TYPE_CLASS, Event.TYPE_OTHER]),
            interested=users
        )
        followers = event.get_followers()
        users_emails = [user.email for user in users]
        self.assertEqual(len(users_emails), len(followers))
        for email in users_emails:
            self.assertTrue(email in followers)

    def test_unicode(self):
        event = factories.EventFactory()
        self.assertEqual('{0} {1}'.format(event.title, event.description), str(event))


class EventsOnChangedDayTestCase(TestCase):
    def find_closest_day_of_week_to_date(self, date, day_of_week):
        date += timedelta(days=1)
        while date.weekday() != day_of_week:
            date += timedelta(days=1)
        return date

    def setUp(self):
        summer_semester = enrollment_factories.SemesterFactory(type=Semester.TYPE_SUMMER)
        summer_semester.full_clean()

        self.thursday = \
            self.find_closest_day_of_week_to_date(summer_semester.semester_beginning, 3)
        changed_day = enrollment_factories.ChangedDayForFridayFactory(
            day=self.thursday
        )
        changed_day.full_clean()

        classroom = enrollment_factories.ClassroomFactory()

        self.reservation_author = factories.UserFactory()
        self.reservation_author.save()
        reservation = factories.SpecialReservationFactory.build(
            semester=summer_semester,
            classroom=classroom
        )
        reservation.full_clean()
        reservation.save(author_id=self.reservation_author.pk)

    def test_add_event_on_changed_day(self):
        classroom = Classroom.get_by_number('25')
        reservation = SpecialReservation.objects.in_classroom(classroom)[0]

        self.assertRaises(
            ValidationError,
            factories.TermThisYearFactory(
                day=self.thursday,
                start=reservation.start_time,
                end=reservation.end_time,
                room=classroom
            ).full_clean
        )

    def test_check_theres_no_original_reservation_on_changed_day(self):
        classroom = Classroom.get_by_number('25')
        reservation = SpecialReservation.objects.in_classroom(classroom)[0]

        reserv_thursday = factories.SpecialReservationFactory.build(
            semester=reservation.semester,
            classroom=classroom,
            start_time=time(16, 15),
            end_time=time(18),
            dayOfWeek=common.THURSDAY
        )
        reserv_thursday.full_clean()
        reserv_thursday.save(author_id=self.reservation_author.pk)

        ev = EventTerm.get_terms_for_dates(
            [self.thursday], classroom, start_time=reserv_thursday.start_time,
            end_time=reserv_thursday.end_time
        )
        self.assertFalse(ev)

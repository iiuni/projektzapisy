import importlib
import json
from typing import List

from django import test
from freezegun import freeze_time

from apps.enrollment.courses.tests import factories as courses
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import RSAKeys, StudentGraded
from apps.users.tests import factories as users

grade_client = importlib.import_module('apps.grade.ticket_create.static.ticket_create.grade-client')


class TicketsTest(test.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.student: users.Student = users.StudentFactory()
        cls.semester: courses.Semester = courses.SemesterFactory(is_grade_active=True)
        course_exam = courses.CourseInstanceFactory(semester=cls.semester)
        course_no_exam = courses.CourseInstanceFactory(semester=cls.semester, has_exam=False)
        cls.groups: List[courses.Group] = [
            courses.GroupFactory(course=course_exam),
            courses.GroupFactory(course=course_no_exam)
        ]

    def test_polls_list(self):
        c = test.Client()
        time_in_semester = self.semester.semester_beginning + (self.semester.semester_ending -
                                                               self.semester.semester_beginning) / 2
        with freeze_time(time_in_semester):
            c.force_login(self.student.user)
            polls = Poll.get_all_polls_for_student(self.student)
            keys = RSAKeys.objects.filter(poll__in=polls)
            self.assertEqual(len(keys), len(polls))
            r = c.get('/grade/ticket/get-poll-data')
            self.assertEqual(len(r.json()), len(polls))

    def test_signing_works(self):
        c = test.Client()
        time_in_semester = self.semester.semester_beginning + (self.semester.semester_ending -
                                                               self.semester.semester_beginning) / 2
        with freeze_time(time_in_semester):
            c.force_login(self.student.user)
            poll_data_r = c.get('/grade/ticket/get-poll-data')

            # Generate blinded tickets.
            poll_data = {d['poll_info']['id']: grade_client.PollData(d) for d in poll_data_r.json()}
            blinded_tickets = grade_client.TicketCreate.get_blinded_tickets_for_signing(
                None, poll_data)
            r = c.post('/grade/ticket/sign-tickets',
                       data=blinded_tickets,
                       content_type='application/json')
            self.assertEqual(r.status_code, 200)
            signed_tickets = r.json()

            # Make sure, we can't sign twice
            poll_data_2 = {d['poll_info']['id']: grade_client.PollData(d) for d in poll_data_r.json()}
            blinded_tickets_2 = grade_client.TicketCreate.get_blinded_tickets_for_signing(
                None, poll_data_2)
            r = c.post('/grade/ticket/sign-tickets',
                       data=blinded_tickets_2,
                       content_type='application/json')
            self.assertEqual(r.status_code, 403)

        # Make sure the student will receive a bonus.
        self.assertTrue(
            StudentGraded.objects.filter(student=self.student, semester=self.semester).exists())

        # Make sure the signed tickets are now accepted.
        unblinded_tickets = []
        for st in signed_tickets:
            poll = poll_data[st['id']]
            unblinded = grade_client.unblind(poll.pub_key, int(st['signature']), poll.ticket.r)
            unblinded_tickets.append({
                'id': poll.id,
                'ticket': str(poll.ticket.m),
                'signature': str(unblinded),
            })
        correct_polls, failed_polls = RSAKeys.parse_raw_tickets(
            json.dumps({'tickets': unblinded_tickets}))
        self.assertEqual(len(correct_polls), len(poll_data))
        self.assertEqual(failed_polls, [])

    def test_cant_double_sign(self):
        c = test.Client()
        time_in_semester = self.semester.semester_beginning + (self.semester.semester_ending -
                                                               self.semester.semester_beginning) / 2
        with freeze_time(time_in_semester):
            c.force_login(self.student.user)
            poll_data_r = c.get('/grade/ticket/get-poll-data')

            # Generate blinded tickets.
            poll_data = {d['poll_info']['id']: grade_client.PollData(d) for d in poll_data_r.json()}
            blinded_tickets = grade_client.TicketCreate.get_blinded_tickets_for_signing(
                None, poll_data)
            # Copy one ticket to make polls match but one appear twice in the list.
            blinded_tickets['signing_requests'].append(blinded_tickets['signing_requests'][0])
            r = c.post('/grade/ticket/sign-tickets',
                       data=blinded_tickets,
                       content_type='application/json')
            self.assertEqual(r.status_code, 403)

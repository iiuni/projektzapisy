from datetime import datetime, timedelta

from django.test import TestCase
from unittest import skip

from apps.grade.poll.models import Poll
from apps.enrollment.courses.tests.factories import CourseFactory, GroupFactory, SemesterFactory
from apps.users.tests.factories import StudentFactory, EmployeeFactory, UserFactory
from apps.grade.ticket_create.utils import generate_keys_for_polls, group_polls_by_course


class UtilsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super(UtilsTest, cls).setUpClass()
        cls.semester = SemesterFactory(is_grade_active=True)
        cls.set_up_users()
        cls.set_up_user_roles()
        cls.set_up_course_groups()
        cls.set_up_polls()
        cls.enroll_students()

    def test_generate_keys_for_polls_generates_keys_for_each_poll(self):
        polls = Poll.objects.all()
        for poll in polls:
            self.assertEqual(list(poll.publickey_set.all()), [])
            self.assertEqual(list(poll.privatekey_set.all()), [])
        generate_keys_for_polls(self.semester)
        for poll in polls:
            self.assertNotEqual(list(poll.publickey_set.all()), [])
            self.assertNotEqual(list(poll.privatekey_set.all()), [])

    @skip("problems with persistence. to be fixed")
    def test_generate_keys_for_polls_generates_keys_for_new_polls_only(self):
        polls = Poll.objects.all()
        generate_keys_for_polls(self.semester)
        for poll in polls:
            self.assertEqual(len(list(poll.publickey_set.all())), 1)
            self.assertEqual(len(list(poll.privatekey_set.all())), 1)

        new_poll = Poll(author=self.employee1, title="test", description="brak",
                        semester=self.semester)
        new_poll.save()
        generate_keys_for_polls(self.semester)

        self.assertEqual(len(list(new_poll.publickey_set.all())), 1)
        self.assertEqual(len(list(new_poll.privatekey_set.all())), 1)
        for poll in polls:
            self.assertEqual(len(list(poll.publickey_set.all())), 1)
            self.assertEqual(len(list(poll.privatekey_set.all())), 1)

    def test_generate_keys_for_polls_do_not_change_saved_keys(self):
        polls = Poll.objects.all()
        generate_keys_for_polls(self.semester)
        pre_keys = []
        for poll in polls:
            c_keys = []
            self.assertEqual(len(list(poll.publickey_set.all())), 1)
            self.assertEqual(len(list(poll.privatekey_set.all())), 1)
            c_keys.append(poll.publickey_set.all()[0])
            c_keys.append(poll.privatekey_set.all()[0])
            pre_keys.append(c_keys)

        generate_keys_for_polls()
        post_keys = []
        for poll in polls:
            c_keys = []
            self.assertEqual(len(list(poll.publickey_set.all())), 1)
            self.assertEqual(len(list(poll.privatekey_set.all())), 1)
            c_keys.append(poll.publickey_set.all()[0])
            c_keys.append(poll.privatekey_set.all()[0])
            post_keys.append(c_keys)

        self.assertEqual(pre_keys, post_keys)

    def test_group_polls_by_course_makes_valid_groups(self):
        generate_keys_for_polls(self.semester)
        polls = Poll.get_all_polls_for_student(self.student1)
        grouped = group_polls_by_course(polls)

        for group in grouped:
            if group[0].group:
                course = group[0].group.course
            else:
                course = None
            for poll in group:
                if course:
                    self.assertEqual(course, poll.group.course)
                else:
                    self.assertEqual(course, poll.group)

    @classmethod
    def set_up_users(cls):
        cls.user1 = UserFactory(is_superuser=True, is_staff=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False)
        cls.user3 = UserFactory(is_superuser=False, is_staff=False)
        cls.user4 = UserFactory(is_superuser=False, is_staff=False)
        cls.user5 = UserFactory(is_superuser=False, is_staff=False)
        cls.user6 = UserFactory(is_superuser=False, is_staff=False)

    @classmethod
    def set_up_user_roles(cls):
        cls.employee1 = EmployeeFactory(user=cls.user2)
        cls.student1 = StudentFactory(user=cls.user3)
        cls.student3 = StudentFactory(user=cls.user5)
        cls.student4 = StudentFactory(user=cls.user6)

    @classmethod
    def set_up_course_groups(cls):
        today = datetime.now()
        course = CourseFactory()
        cls.group1 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
            type="1"
        )
        cls.group2 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
            type="2"
        )
        cls.group3 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
            type="3"
        )
        cls.group4 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
            type="3"
        )

    @classmethod
    def enroll_students(cls):
        cls.group1.add_student(cls.student1)
        cls.group1.add_student(cls.student3)
        cls.group1.add_student(cls.student4)
        cls.group1.save()

        cls.group3.add_student(cls.student1)
        cls.group3.save()

        cls.group4.add_student(cls.student1)
        cls.group4.save()

    @classmethod
    def set_up_polls(cls):
        cls.poll1 = Poll(semester=cls.semester, group=None, author=cls.employee1, deleted=False)
        cls.poll1.save()
        cls.poll2 = Poll(semester=cls.semester, group=None, author=cls.employee1, deleted=False)
        cls.poll2.save()
        cls.poll3 = Poll(semester=cls.semester, group=cls.group1, author=cls.employee1, deleted=False)
        cls.poll3.save()
        cls.poll4 = Poll(semester=cls.semester, group=cls.group2, author=cls.employee1, deleted=False)
        cls.poll4.save()
        cls.poll5 = Poll(semester=cls.semester, group=cls.group3, author=cls.employee1, deleted=False)
        cls.poll5.save()

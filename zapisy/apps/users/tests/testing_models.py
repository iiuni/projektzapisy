
# tests marked by comment "TIME DEPENDENCY" should be free from this dependency



from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from apps.users.models import Employee, Student, StudiaZamawiane
from django.contrib.auth.models import Permission
from django.db import connection

from random import randint
from apps.enrollment.courses.models import Semester
from datetime import datetime, timedelta


# class EmployeeGroupsTest(TestCase):
#     fixtures =  ['fixtures__users', 'fixtures__courses']

#     def setUp(self):
#         self.user = User.objects.get(id=4)

#     def testWithNotEmployeeUser(self):
#         self.user.employee.delete()
#         self.assertRaises(NonEmployeeException, Employee.get_all_groups, 4)

#     def testEmployeeGroups(self):
#         groups = Employee.get_all_groups(self.user.id)
#         groups_id = [g.id for g in groups]
#         self.assertEquals(groups_id, [1, 3, 5])

# class EmployeeScheduleTest(TestCase):
#     fixtures =  ['fixtures__users', 'fixtures__courses']

#     def setUp(self):
#         self.user = User.objects.get(id=4)

#     def testWithNotEmployeeUser(self):
#         self.user.employee.delete()
#         self.assertRaises(NonEmployeeException, Employee.get_schedule, self.user.id)

# #TIME DEPENDENCY
#     def testEmployeeSchedule(self):
#         course_1 = Course.objects.get(id=1)

#         groups = Employee.get_schedule(self.user.id)

#         term_1 = Term.objects.get(id=1).id
#         term_2 = Term.objects.get(id=3).id

#         groups_id = [g.id for g in groups]
#         groups_course = [g.course_ for g in groups]
#         groups_term_id = []
#         groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
#         groups_term_id = map(lambda x: x.id, groups_term_id)

#         for g in groups_id:
#               self.assert_(g in [1, 3, 5])
#         for s in groups_course:
#               self.assert_(s in [course_1, course_1])
#         for t in groups_term_id:
#               self.assert_(t in [term_1, term_2])

# class StudentScheduleTest(TestCase):
#     fixtures =  ['fixtures__users', 'fixtures__courses']

#     def setUp(self):
#       """
#       EXERCISE_GROUP:
#               "fields": {
#                   "limit": 120,
#                   "type": "2",
#                   "teacher": 3,
#                   "course": 1
#               }
#           LECTURE_GROUP:
#                   "fields": {
#                   "limit": 120,
#                   "type": "1",
#                   "teacher": 3,
#                   "course": 1
#               }
#       """
#         self.user = User.objects.get(id=5)
#         self.exercise_group = Group.objects.get(id=1)
#         self.lecture_group = Group.objects.get(id=3)
#         self.lecture_group_2 = Group.objects.get(id=5)
#         #Automaticaly add student to lecture group
#         self.record = Record.add_student_to_group(self.user, self.exercise_group)

#    def testWithNotStudentUser(self):
#        TODO: function changes, change test
#        self.user.student.delete()
#
#        self.assertRaises(NonStudentException, Student.get_schedule, self.user.student)

#TIME DEPENDENCY
    # def testStudentSchedule(self):
    #     course_1 = Course.objects.get(id=1)
    #     course_1.semester.date = datetime.now().year
    #     course_1.semester.semester_begining = date.today()
    #     course_1.semester.semester_ending = date.today() + timedelta(days = 5 * 30)
    #     course_1.semester.save()

    #     groups = Student.get_schedule(self.user.student)

    #     term_1 = Term.objects.get(id=1).id
    #     term_2 = Term.objects.get(id=3).id

    #     groups_id = [g.id for g in groups]
    #     groups_course = [g.course_ for g in groups]
    #     groups_term_id = []
    #     groups_term = [groups_term_id.extend(t) for t in [g.terms_ for g in groups]]
    #     groups_term_id = map(lambda x: x.id, groups_term_id)

    #     for g in groups_id:
    #           self.assert_(g in [self.exercise_group.id, self.lecture_group.id, self.lecture_group_2.id])
    #     for s in groups_course:
    #           self.assert_(s in [course_1, course_1])
    #     for t in groups_term_id:
    #           self.assert_(t in [term_1, term_2])

class IBANTest(TestCase):
    def setUp(self):
        self.not_alphanum = 'PL0810&000049916589081209234'
        self.invalid_polish = 'PL08119000049916589081209234'
        self.invalid_without_country_code = '08109000039916589081209234'
        self.invalid_polish_wrong_length= '0810900003991658908120923'
        self.valid_polish = 'PL08109000049916589081209234'
        self.valid_polish_without_country_code = '08109000049916589081209234'
        self.valid_polish_spaced = '17 1140 2004 0000 3202 5905 0681'
        self.valid_greece = 'GR16 0110 1250 0000 0001 2300 695'

    def testWithNotAlphaNumeric(self):
        self.assertFalse(StudiaZamawiane.check_iban(self.not_alphanum))

    def testWithInvalidPolish(self):
        self.assertFalse(StudiaZamawiane.check_iban(self.invalid_polish))

    def testWithInvalidWithoutCountryCode(self):
        self.assertFalse(StudiaZamawiane.check_iban(self.invalid_without_country_code))

    def testWithPolishWithWrongLength(self):
        self.assertFalse(StudiaZamawiane.check_iban(self.invalid_polish_wrong_length))

    def testWithValidPolish(self):
        self.assertTrue(StudiaZamawiane.check_iban(self.valid_polish))

    def testWithValidSpaced(self):
        self.assertTrue(StudiaZamawiane.check_iban(self.valid_polish_spaced))

    def testWithValidPolishWithoutCountryCode(self):
        self.assertTrue(StudiaZamawiane.check_iban(self.valid_polish_without_country_code))

    def testWithValidGreece(self):
        self.assertTrue(StudiaZamawiane.check_iban(self.valid_greece))

class MailsToStudentsLinkTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
            ]

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)

        cls.MSG_HEADER = 'Wyślij wiadomość do studentów'
        regular_user = User.objects.create_user('regular_user', 'user@user.com', 'password')
        Student.objects.create(user=regular_user)
        cls.regular_user = regular_user

        permission = Permission.objects.get(codename='mailto_all_students')
        dean_user = User.objects.create_user('dean_user', 'user@user.com', 'password')
        dean_user.user_permissions.add(permission)
        cls.dean_user = dean_user

        from apps.enrollment.courses.tests.factories import SemesterFactory
        summer_semester = SemesterFactory(type=Semester.TYPE_SUMMER)
        summer_semester.full_clean()

    @classmethod
    def tearDownTestData(cls):
        sql_calls = [
            "DROP TABLE courses_studentpointsview;",
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)

    def test_mailto_link_not_exists_regular_user(self):
        self.client.login(username='regular_user', password='password')
        response = self.client.get(reverse('my-profile'))
        #print(response)
        self.assertNotContains(response, self.MSG_HEADER, status_code=200)

    def test_mailto_link_exists_dean_user(self):
        self.client.login(username='dean_user', password='password')
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, self.MSG_HEADER, status_code=200)


class MyProfileSemesterInfoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
            ]

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)

        student_user = User.objects.create_user('student_user', 'student@user.com', 'password')
        s = Student.objects.create(user=student_user, matricula=str(randint(100000, 200000)))
        student_user.save()
        s.save()

        Semester.objects.all().delete()
        cls.semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            records_opening=datetime.now()-timedelta(days=15),
            records_closing=datetime.now()+timedelta(days=15),
            records_ects_limit_abolition=datetime.now()+timedelta(days=5),
            semester_beginning=datetime.now()+timedelta(days=20),
            semester_ending=datetime.now()+timedelta(days=100)
        )
        cls.semester.full_clean()
        cls.semester.save()

    @classmethod
    def tearDownTestData(cls):
        sql_calls = [
            "DROP TABLE courses_studentpointsview;",
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def test_my_profile_contains_records_closing_time(self):
        self.semester.records_ending = datetime.now()+timedelta(days=10)
        self.semester.save()
        self.client.login(username='student_user', password='password')
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, "Koniec wypisów", status_code=200)

    def test_my_profile_does_not_contain_records_closing_time(self):
        self.semester.records_ending = None
        self.semester.save()
        self.client.login(username='student_user', password='password')
        response = self.client.get(reverse('my-profile'))
        self.assertNotContains(response, "Koniec wypisów", status_code=200)

    def test_my_profile_contains_other_semester_info(self):
        self.client.login(username='student_user', password='password')
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, "Zniesienie limitu 35 ECTS")
        self.assertContains(response, "Koniec zapisów")

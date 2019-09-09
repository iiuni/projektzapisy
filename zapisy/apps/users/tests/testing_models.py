# tests marked by comment "TIME DEPENDENCY" should be free from this dependency


from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import Permission
from django.db import connection

from random import randint
from apps.enrollment.courses.models.semester import Semester
from datetime import datetime, timedelta

from apps.users.tests.factories import StudentFactory, EmployeeFactory


class MailsToStudentsLinkTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:

        cls.MSG_HEADER = 'Wyślij wiadomość do studentów'
        regular_user = StudentFactory()
        cls.regular_user = regular_user.user

        permission = Permission.objects.get(codename='mailto_all_students')
        dean_user = EmployeeFactory()
        dean_user.user.user_permissions.add(permission)
        cls.dean_user = dean_user.user

        from apps.enrollment.courses.tests.factories import SemesterFactory
        summer_semester = SemesterFactory(type=Semester.TYPE_SUMMER)
        summer_semester.full_clean()

    def test_mailto_link_not_exists_regular_user(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('my-profile'))
        self.assertNotContains(response, self.MSG_HEADER, status_code=200)

    def test_mailto_link_exists_dean_user(self):
        self.client.force_login(self.dean_user)
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, self.MSG_HEADER, status_code=200)


class MyProfileSemesterInfoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        s = StudentFactory()
        s.matricula = str(randint(100000, 200000))
        cls.student_user = s.user

        Semester.objects.all().delete()
        cls.semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            records_opening=datetime.now() - timedelta(days=15),
            records_closing=datetime.now() + timedelta(days=15),
            records_ects_limit_abolition=datetime.now() + timedelta(days=5),
            semester_beginning=datetime.now() + timedelta(days=20),
            semester_ending=datetime.now() + timedelta(days=100)
        )
        cls.semester.full_clean()
        cls.semester.save()

    def test_my_profile_contains_records_closing_time(self) -> None:
        self.semester.records_ending = datetime.now() + timedelta(days=10)
        self.semester.save()
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, "Koniec wypisów", status_code=200)

    def test_my_profile_does_not_contain_records_closing_time(self) -> None:
        self.semester.records_ending = None
        self.semester.save()
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('my-profile'))
        self.assertNotContains(response, "Koniec wypisów", status_code=200)

    def test_my_profile_contains_other_semester_info(self) -> None:
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('my-profile'))
        self.assertContains(response, "Zniesienie limitu 35 ECTS")
        self.assertContains(response, "Koniec zapisów")

import re
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase

from apps.enrollment.courses.models import Semester
from parameterized import parameterized


class AdminTestCase(TestCase):
    SUB_PAGES = [
        "/fereol_admin/courses/freeday/",
        "/fereol_admin/courses/changedday/",
        "/fereol_admin/courses/group/",
        "/fereol_admin/courses/effects/",
        "/fereol_admin/courses/courseinstance/",
        "/fereol_admin/courses/type/",
        "/fereol_admin/courses/classroom/",
        "/fereol_admin/courses/semester/",
        "/fereol_admin/courses/tag/",
        "/fereol_admin/desiderata/desiderataother/",
        "/fereol_admin/desiderata/desiderata/",
        "/fereol_admin/mailer/dontsendentry/",
        "/fereol_admin/mailer/messagelog/",
        "/fereol_admin/mailer/message/",
        "/fereol_admin/news/news/",
        "/fereol_admin/poll/template/",
        "/fereol_admin/poll/savedticket/",
        "/fereol_admin/preferences/preference/",
        "/fereol_admin/schedule/specialreservation/",
        "/fereol_admin/schedule/term/",
        "/fereol_admin/sites/site/",
        "/fereol_admin/ticket_create/privatekey/",
        "/fereol_admin/ticket_create/publickey/",
        "/fereol_admin/ticket_create/studentgraded/",
        "/fereol_admin/ticket_create/usedticketstamp/",
        "/fereol_admin/users/employee/",
        "/fereol_admin/users/program/",
        "/fereol_admin/users/student/",
        "/fereol_admin/auth/group/",
        "/fereol_admin/auth/user/",
        "/fereol_admin/vote/systemstate/"]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.password = 'pass'
        cls.admin = User.objects.create_superuser(username='przemka',
                                                  password=cls.password,
                                                  email='admin@admin.com')
        cls.admin.first_name = 'przemka'
        cls.admin.save()
        today = datetime.now()
        cls.semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            year='2016/17',
            records_opening=(today + timedelta(days=-1)),
            records_closing=today + timedelta(days=6),
            lectures_beginning=today + timedelta(days=4),
            lectures_ending=today + timedelta(days=120),
            semester_beginning=today,
            semester_ending=today + timedelta(days=130),
            records_ects_limit_abolition=(today + timedelta(days=1)))
        cls.semester.save()

        cls.client = Client()

    @classmethod
    def tearDownTestData(cls) -> None:
        cls.admin.delete()
        cls.semester.delete()

    @parameterized.expand(SUB_PAGES)
    def test_subpages(self, link_text: str) -> None:
        self.client.post("/fereol_admin/login/", {"username": self.admin.username, "password": self.password},
                         follow=True)
        # For some unknown for me reasons, logging in at set up won't be enough, and we have to log in for each test
        response = self.client.get(link_text, follow=True)
        assert('user-tools' in str(response.content))
        self.client.get("/fereol_admin/logout/", follow=True)

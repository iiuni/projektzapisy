# -*- coding: utf-8 -*-

# Run this tests with 'xvfb-run python manage.py test test_app' command

from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementNotVisibleException,
    NoSuchElementException,
    TimeoutException,
)

from django.contrib.auth.models import User
from apps.users.models import Employee, Student
from apps.enrollment.courses.models import Semester, CourseEntity, Course, Type, Group, Term, Classroom
from apps.offer.vote.models import SystemState

import os
from time import sleep
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.db import connection

from django.conf import settings
from scripts.scheduleimport import run_test as scheduleimport_run_test
from scripts.ectsimport import run_test as ectsimport_run_test


class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.set_window_size(1024, 1024)
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def wait_for_pass(self, block, times=3):
        for _ in xrange(times):
            try:
                return block()
            except (ElementNotVisibleException, NoSuchElementException, TimeoutException):
                sleep(3)
        return block()



class NewSemesterTests(SeleniumTestCase):

    def setUp(self):
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
            connection.commit()

        self.password = '11111'
        self.admin = User.objects.create_superuser(username='przemka',
                                                   password=self.password,
                                                   email='admin@admin.com')
        self.admin.first_name = 'przemka'
        self.admin.save()
        self.employee = Employee.objects.create(user=self.admin)

        self.employees = []
        for i in range(1, 5):
            user = User.objects.create_user(
                username=('employee{}'.format(i)),
                password=self.password)
            user.first_name = 'Employee'
            user.last_name = str(i)
            user.save()
            employee = Employee.objects.create(user=user)
            self.employees.append(employee)

        user_student1 = User.objects.create_user(
            username='student1',
            password=self.password)
        user_student2 = User.objects.create_user(
            username='student2',
            password=self.password)
        user_student3 = User.objects.create_user(
            username='student3',
            password=self.password)
        user_student4 = User.objects.create_user(
            username='student4',
            password=self.password)
        self.student1 = Student.objects.create(
            user=user_student1, matricula='264823')
        self.student2 = Student.objects.create(
            user=user_student2, matricula='222222')
        self.student3 = Student.objects.create(
            user=user_student3, matricula='333333')
        self.student4 = Student.objects.create(
            user=user_student4, matricula='444444')

        self.course_type = Type.objects.create(name='Informatyczny')
        for i in range(1, 6):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='z',
                type=self.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        for i in range(6, 11):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='l',
                type=self.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        CourseEntity.objects.create(
            name='Course 50',
            semester='l',
            type=self.course_type,
            status=0,  # propozycja
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 100',
            semester='z',
            type=self.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 101',
            semester='l',
            type=self.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        for course_entity in CourseEntity.objects.all():
            course_entity.owner = self.employee
            course_entity.save()

        self.winter_courses = ['Course 1', 'Course 2', 'Course 3']

        self.current_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='1',
            semester_beginning=date.today(),
            semester_ending=date.today() + relativedelta(months=3),
            records_ects_limit_abolition=date.today() + relativedelta(days=10),
            visible=True,
            is_grade_active=False
        )

        self.next_winter_semester = Semester.objects.create(
            type=Semester.TYPE_WINTER,
            year='2',
            semester_beginning=self.current_semester.semester_ending + relativedelta(days=1),
            semester_ending=self.current_semester.semester_ending + relativedelta(days=1, months=3),
            records_ects_limit_abolition=self.current_semester.semester_ending + relativedelta(days=11),
            visible=True,
            is_grade_active=False
        )

        self.next_summer_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='3',
            semester_beginning=self.next_winter_semester.semester_ending + relativedelta(days=1),
            semester_ending=self.next_winter_semester.semester_ending + relativedelta(days=1, months=3),
            records_ects_limit_abolition=self.next_winter_semester.semester_ending + relativedelta(days=11),
            visible=True,
            is_grade_active=False
        )

        self.system_state = SystemState.objects.create(
            semester_winter=self.next_winter_semester,
            semester_summer=self.next_summer_semester,
            max_points=12,
            max_vote=3
        )

    def tearDown(self):
        sql_calls = [
            'DROP TABLE courses_studentpointsview;',
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def test_new_semester_scenario(self):
        self.prepare_course_entities_for_voting()
        self.perform_voting()
        self.create_offer_for_winter_semester()
        self.perform_winter_correction()
        self.import_winter_schedule()
        self.start_winter_semester()
        self.add_new_students()
        self.import_ects()
        self.open_records()
        self.generate_t0()

        self.driver.get_screenshot_as_file('screenshot.png')

    def prepare_course_entities_for_voting(self):
        self.driver.get(self.live_server_url)
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'login-dropdown').click()
                )
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'btn-no-usos').click()
                )
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_login').send_keys(
                    self.admin.username))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_password').send_keys(
                    self.password))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//button[contains(text(), "Zaloguj")]').click()
                )
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Oferta').click())
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Zarządzaj').click())
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Głosowanie').click())

        nonselected_select = Select(
            self.wait_for_pass(lambda: WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.ID, 'bootstrap-duallistbox-nonselected-list_for_voting'))))
        )
        # nonselected_select =
        # Select(self.driver.find_element_by_id('bootstrap-duallistbox-nonselected-list_for_voting'))
        selected_select = Select(
            self.wait_for_pass(
                lambda: self.driver.find_element_by_id(
                    'bootstrap-duallistbox-selected-list_for_voting')))
        self.assertEqual(
            CourseEntity.objects.filter(status=1).count(),
            len(nonselected_select.options))
        self.assertEqual(
            CourseEntity.objects.filter(status=2).count(),
            len(selected_select.options))

        for ce in CourseEntity.objects.filter(status=1):
            if ce.name != 'Course 100' and ce.name != 'Course 101':
                nonselected_select.select_by_visible_text(ce.name)

        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//input[@value="Zapisz"]').click(
            ))

        nonselected_select = Select(
            self.wait_for_pass(
                lambda: self.driver.find_element_by_id(
                    'bootstrap-duallistbox-nonselected-list_for_voting')))
        selected_select = Select(
            self.wait_for_pass(
                lambda: self.driver.find_element_by_id(
                    'bootstrap-duallistbox-selected-list_for_voting')))
        self.assertEqual(
            CourseEntity.objects.filter(status=1).count(),
            len(nonselected_select.options))
        self.assertEqual(
            CourseEntity.objects.filter(status=2).count(),
            len(selected_select.options))

    def perform_voting(self):
        # voting starts
        self.system_state.vote_beg = date.today()
        self.system_state.vote_end = date.today() + relativedelta(days=1)
        self.system_state.save()

        self.results_points = defaultdict(int)
        self.results_votes = defaultdict(int)
        self.vote(
            self.student1,
            {'Course 1': 3, 'Course 2': 3, 'Course 3': 3, 'Course 4': 3,
             'Course 5': 3, 'Course 6': 3, 'Course 7': 3, 'Course 8': 3,
             'Course 9': 3, 'Course 10': 3}
        )
        self.vote(
            self.student1,
            {'Course 1': 1, 'Course 2': 2, 'Course 4': 3, 'Course 5': 2,
             'Course 6': 2, 'Course 7': 1, 'Course 8': 1}
        )
        self.vote(
            self.student2,
            {'Course 1': 2, 'Course 2': 1, 'Course 3': 3, 'Course 4': 2,
             'Course 8': 1, 'Course 9': 1, 'Course 10': 2}
        )
        self.vote(
            self.student3,
            {'Course 1': 3, 'Course 3': 1, 'Course 4': 2, 'Course 6': 2,
             'Course 8': 2, 'Course 10': 2}
        )
        self.vote(
            self.student4,
            {'Course 2': 1, 'Course 3': 2, 'Course 5': 2, 'Course 7': 3,
             'Course 8': 1, 'Course 9': 1, 'Course 10': 2}
        )

        # check voting results
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Głosowanie').click())
        self.wait_for_pass(lambda: WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Podsumowanie głosowania'))).click())
        rows = self.wait_for_pass(
            lambda: self.driver.find_elements_by_xpath('//table/tbody/tr'))
        for row in rows:
            cells = row.find_elements_by_tag_name('td')
            self.assertEqual(
                self.results_points[cells[0].text],
                int(cells[1].text))
            self.assertEqual(
                self.results_votes[cells[0].text],
                int(cells[2].text))

        # voting ends
        self.system_state.vote_beg = date.today() - relativedelta(days=2)
        self.system_state.vote_end = date.today() - relativedelta(days=1)
        self.system_state.save()

    def vote(self, student, points):
        self.driver.get('{}{}'.format(self.live_server_url, '/users/logout/'))
        self.driver.get(self.live_server_url)
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'login-dropdown').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'btn-no-usos').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_login').send_keys(
                    student.user.username))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_password').send_keys(
                    self.password))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//button[contains(text(), "Zaloguj")]').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Oferta').click())
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Głosowanie').click())
        self.wait_for_pass(lambda: WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Głosuj'))).click())

        sum_points = sum(points.values())

        for course_name, value in points.items():
            select = Select(
                self.wait_for_pass(
                    lambda: self.driver.find_element_by_xpath(
                        '//li[label/a[text()="{}"]]/select'.format(course_name))))
            select.select_by_value(str(value))
            if sum_points <= self.system_state.max_points:
                self.results_points[course_name] += value
                self.results_votes[course_name] += 1

        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//input[@value="Głosuj"]').click(
            ))

        if sum_points <= self.system_state.max_points:
            self.assertEqual(
                len(self.driver.find_elements_by_xpath(
                    '//div[contains(text(), "Oddano poprawny głos")]')),
                1)
        else:
            self.assertEqual(
                len(self.driver.find_elements_by_xpath(
                    '//div[contains(text(), "Nie udało się oddać głosu")]')),
                1)

    def create_offer_for_winter_semester(self):
        for course in self.winter_courses:
            Course.objects.create(
                entity=CourseEntity.objects.get(name=course),
                semester=self.next_winter_semester
            )

    def perform_winter_correction(self):
        # winter correction starts
        self.system_state.winter_correction_beg = date.today()
        self.system_state.winter_correction_end = date.today() + relativedelta(
            days=1)
        self.system_state.save()

        self.correction(
            self.student1,
            {'Course 1': 3, 'Course 3': 3}
        )
        self.correction(
            self.student2,
            {'Course 2': 3}
        )
        self.correction(
            self.student3,
            {'Course 2': 2}
        )
        self.correction(
            self.student4,
            {'Course 1': 1, 'Course 2': 2}
        )

        # winter correction ends
        self.system_state.winter_correction_beg = date.today() - relativedelta(
            days=2)
        self.system_state.winter_correction_end = date.today() - relativedelta(
            days=1)
        self.system_state.save()

    def correction(self, student, points):
        self.driver.get('{}{}'.format(self.live_server_url, '/users/logout/'))
        self.driver.get(self.live_server_url)
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'login-dropdown').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'btn-no-usos').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_login').send_keys(
                    student.user.username))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id(
                'id_password').send_keys(
                    self.password))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//button[contains(text(), "Zaloguj")]').click(
            ))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Oferta').click())
        self.wait_for_pass(
            lambda: self.driver.find_element_by_link_text('Głosowanie').click())
        self.wait_for_pass(lambda: WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Głosuj'))).click())

        for course_name, value in points.items():
            select = Select(
                self.wait_for_pass(
                    lambda: self.driver.find_element_by_xpath(
                        '//li[label/a[text()="{}"]]/select'.format(course_name))
                    )
            )
            select.select_by_value(str(value))

        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(
                '//input[@value="Głosuj"]').click(
            ))

    def import_winter_schedule(self):
        courses = {}
        for course in Course.objects.filter(semester=self.next_winter_semester):
            courses[course.entity.name] = course.id

        employees = {'{} {}'.format(empl.user.first_name, empl.user.last_name): empl.id for empl in self.employees}

        Classroom.objects.create(number=5, type=1)
        Classroom.objects.create(number=7, type=3)
        Classroom.objects.create(number=25, type=0)
        Classroom.objects.create(number=103, type=1)
        Classroom.objects.create(number=104, type=1)
        Classroom.objects.create(number=105, type=1)
        Classroom.objects.create(number=108, type=3)
        Classroom.objects.create(number=119, type=0)
        Classroom.objects.create(number=139, type=1)

        test_schedule = '''

 Course 1
  pn  16-18  (cwiczenia) Employee 4, sala 103
  wt  14-16  (cwiczenia) Employee 2, sala 139
  sr  8-10   (wyklad) Employee 1, sala 25
  sr  12-14  (cwiczenia) Employee 1, sala 139
  czw 8-10   (cwiczenia) Employee 3, sala 105
  czw 14-16  (repetytorium) Employee 2, sala 104

 Course 2
  pn  10-12  (cwicz+pracownia) Employee 5, sale 105,108
  wt  14-16  (cwicz+pracownia) Employee 3, sale 5,108
  wt  16-18  (wyklad) Employee 2, sala 119
  czw 16-18  (cwicz+pracownia) Employee 5, sale 5,7

 Course 3
  czw 12-14  (seminarium) Employee 4, sala 119

'''

        test_schedule_path = settings.BASE_DIR + '/test_schedule.txt'
        with open(test_schedule_path, 'w') as file:
            file.write(test_schedule)
        scheduleimport_run_test(
            test_schedule_path,
            courses,
            employees,
            self.next_winter_semester.id)

        os.remove(test_schedule_path)

        groups = Group.objects.all()
        self.assertEqual(
            groups.filter(course__entity__name='Course 1').count(),
            6)
        self.assertEqual(
            groups.filter(course__entity__name='Course 2').count(),
            4)
        self.assertEqual(
            groups.filter(course__entity__name='Course 3').count(),
            1)

        terms = Term.objects.select_related('group').all()
        self.assertEqual(
            terms.filter(
                group__course__entity__name='Course 1',
                group__teacher__user__first_name='Employee',
                group__teacher__user__last_name='4',
                group__type=2,
                classrooms__number__in=[103],
                dayOfWeek=1,
                start_time=time(hour=16),
                end_time=time(hour=18)).count(),
            1)

    def start_winter_semester(self):
        self.current_semester.semester_beginning = date.today() - relativedelta(
            days=3)
        self.current_semester.records_ects_limit_abolition = date.today() - relativedelta(
            days=2)
        self.current_semester.semester_ending = date.today() - relativedelta(
            days=1)
        self.current_semester.save()

        self.next_winter_semester.semester_beginning = date.today()
        self.next_winter_semester.records_ects_limit_abolition = date.today() + relativedelta(
            days=11)
        self.next_winter_semester.semester_ending = date.today() + relativedelta(
            months=3)
        self.next_winter_semester.save()

    def add_new_students(self):
        number_of_students = Student.objects.all().count()
        self.new_students = []
        for i in range(1, 6):
            user = User.objects.create_user(
                username='student{}'.format(i + number_of_students), password=self.password)
            student = Student.objects.create(
                user=user,
                matricula=str(i + number_of_students))
            self.new_students.append(student)

    def import_ects(self):
        students_ects = {
            self.student1: {'I': 179},
            self.student2: {'I': 185, 'II': 55},
            self.student3: {'I': 64},
            self.student4: {'I': 190, 'II': 80}
        }

        test_ectsimport = ''
        for student, points in students_ects.items():
            for deg, ects in points.items():
                test_ectsimport += '{} {} T {} stopnia\n'.format(student.matricula, ects, deg)

        test_ectsimport_path = settings.BASE_DIR + '/test_ectsimport.txt'
        with open(test_ectsimport_path, 'w') as file:
            file.write(test_ectsimport)

        ectsimport_run_test(test_ectsimport_path)

        os.remove(test_ectsimport_path)

        for student in Student.objects.all():
            if student in students_ects:
                ects_sum = sum(students_ects[student].values())
                self.assertEqual(ects_sum, student.ects)

    def open_records(self):
        self.next_winter_semester.records_opening = datetime.today().replace(
            hour=00, minute=00)
        self.next_winter_semester.records_closing = self.next_winter_semester.records_opening + \
            relativedelta(days=10)
        self.next_winter_semester.save()

    def generate_t0(self):
        # cursor = connection.cursor()
        # cursor.execute('SELECT
        # users_openingtimesview_refresh_for_semester(%s)',
        # [self.next_winter_semester.id])
        pass


class AdminTests(SeleniumTestCase):

    SUB_PAGES = [
      "/fereol_admin/courses/freeday/", "/fereol_admin/courses/changedday/", "/fereol_admin/courses/group/",
      "/fereol_admin/courses/effects/", "/fereol_admin/courses/coursedescription/",
      "/fereol_admin/courses/courseentity/", "/fereol_admin/courses/course/", "/fereol_admin/courses/type/",
      "/fereol_admin/courses/pointtypes/", "/fereol_admin/courses/classroom/", "/fereol_admin/courses/semester/",
      "/fereol_admin/courses/tag/", "/fereol_admin/courses/pointsofcourseentities/",
      "/fereol_admin/desiderata/desiderataother/", "/fereol_admin/desiderata/desiderata/",
      "/fereol_admin/mailer/dontsendentry/", "/fereol_admin/mailer/messagelog/", "/fereol_admin/mailer/message/",
      "/fereol_admin/news/news/", "/fereol_admin/notifications/notificationpreferences/",
      "/fereol_admin/poll/template/",
      "/fereol_admin/poll/savedticket/", "/fereol_admin/preferences/preference/",
      "/fereol_admin/schedule/specialreservation/", "/fereol_admin/schedule/term/", "/fereol_admin/sites/site/",
      "/fereol_admin/ticket_create/privatekey/", "/fereol_admin/ticket_create/publickey/",
      "/fereol_admin/ticket_create/studentgraded/", "/fereol_admin/ticket_create/usedticketstamp/",
      "/fereol_admin/users/employee/", "/fereol_admin/users/program/", "/fereol_admin/users/student/",
      "/fereol_admin/users/studiazamawianemaileopiekunow/", "/fereol_admin/users/studiazamawiane/",
      "/fereol_admin/users/studiazamawiane2012/", "/fereol_admin/auth/group/", "/fereol_admin/auth/user/",
      "/fereol_admin/vote/singlevote/", "/fereol_admin/vote/systemstate/"
      ]

    def createAdmin(self):
        self.password = '11111'
        self.admin = User.objects.create_superuser(username='przemka',
                                                   password=self.password,
                                                   email='admin@admin.com')
        self.admin.first_name = 'przemka'
        self.admin.save()
    def createSemester(self):
       today = datetime.now()
       self.semester = Semester(
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
       self.semester.save()

    def setUp(self):
        self.createAdmin()
        self.createSemester()
        self.driver.get('{}/fereol_admin'.format(self.live_server_url))
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id('id_username').send_keys(self.admin.username)
            )
        self.wait_for_pass(
            lambda: self.driver.find_element_by_id('id_password').send_keys(self.password)
            )
        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath('//input[@type="submit"]').click()
            )

    def tearDown(self):
        self.admin.delete()
        self.semester.delete()

    def testAdminLogin(self):
        self.wait_for_pass(lambda: self.driver.find_element_by_id('user-tools'))


def createSubPageTest(link_text):
    def f(self):
        self.wait_for_pass(
            lambda: self.driver.find_element_by_xpath(u'//th//a[@href="{}"]'.format(link_text)).click()
            )
        self.wait_for_pass(lambda: self.driver.find_element_by_id('user-tools'))
    return f


for idx, name in enumerate(AdminTests.SUB_PAGES):
    setattr(AdminTests, 'testSubpageId' + str(idx), createSubPageTest(name))

from django.test import LiveServerTestCase

from django.contrib.auth.models import User, Group as UserGroup
from apps.users.models import Employee, Student, PersonalDataConsent
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.course import CourseEntity, Course
from apps.enrollment.courses.models.course_type import Type
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.term import Term
from apps.enrollment.courses.models.classroom import Classroom
from apps.offer.vote.models import SystemState
from apps.offer.vote.vote_form import VoteFormset

import os, re
from time import sleep
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.db import connection
from django.core import mail

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from scripts.scheduleimport import run_test as scheduleimport_run_test
from scripts.ectsimport import run_test as ectsimport_run_test


class NewSemestrTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        sql_calls = [
            """
                CREATE TABLE courses_studentpointsview (
                    value smallint,
                    student_id integer,
                    entity_id integer
                );
            """
        ]

        students, _ = UserGroup.objects.get_or_create(name='students')
        employees, _ = UserGroup.objects.get_or_create(name='employees')

        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)

        cls.password = '11111'
        cls.admin = User.objects.create_superuser(
            username='przemka', password=cls.password, email='admin@admin.com')

        cls.admin.first_name = 'przemka'
        cls.admin.save()
        employees.user_set.add(cls.admin)
        cls.employee = Employee.objects.create(user=cls.admin)

        cls.employees = []
        for i in range(1, 5):
            user = User.objects.create_user(
                username=('employee{}'.format(i)), password=cls.password)
            user.first_name = 'Employee'
            user.last_name = str(i)
            user.save()
            employees.user_set.add(user)
            employee = Employee.objects.create(user=user)
            cls.employees.append(employee)
        employees.save()

        user_student1 = User.objects.create_user(
            username='student1', password=cls.password)
        user_student2 = User.objects.create_user(
            username='student2', password=cls.password)
        user_student3 = User.objects.create_user(
            username='student3', password=cls.password)
        user_student4 = User.objects.create_user(
            username='student4', password=cls.password)

        students.user_set.add(user_student1)
        students.user_set.add(user_student2)
        students.user_set.add(user_student3)
        students.user_set.add(user_student4)
        students.save()

        cls.student1 = Student.objects.create(
            user=user_student1, matricula='264823')
        cls.student2 = Student.objects.create(
            user=user_student2, matricula='222222')
        cls.student3 = Student.objects.create(
            user=user_student3, matricula='333333')
        cls.student4 = Student.objects.create(
            user=user_student4, matricula='444444')
        PersonalDataConsent.objects.update_or_create(
            student=cls.student1, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student2, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student3, defaults={'granted': True})
        PersonalDataConsent.objects.update_or_create(
            student=cls.student4, defaults={'granted': True})
        cls.course_type = Type.objects.create(name='Informatyczny')
        for i in range(1, 6):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='z',
                type=cls.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        for i in range(6, 11):
            CourseEntity.objects.create(
                name='Course {}'.format(i),
                name_pl='Course {}'.format(i),
                name_en='Course {}'.format(i),
                semester='l',
                type=cls.course_type,
                status=1,  # w ofercie
                suggested_for_first_year=False,
            )
        CourseEntity.objects.create(
            name='Course 50',
            semester='l',
            type=cls.course_type,
            status=0,  # propozycja
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 100',
            semester='z',
            type=cls.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        CourseEntity.objects.create(
            name='Course 101',
            semester='l',
            type=cls.course_type,
            status=1,  # w ofercie
            suggested_for_first_year=False,
        )

        for course_entity in CourseEntity.objects.all():
            course_entity.owner = cls.employee
            course_entity.save()

        cls.winter_courses = ['Course 1', 'Course 2', 'Course 3']

        cls.current_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='1',
            semester_beginning=date.today(),
            semester_ending=date.today() + relativedelta(months=3),
            records_ects_limit_abolition=date.today() + relativedelta(days=10),
            visible=True,
            is_grade_active=False)

        cls.next_winter_semester = Semester.objects.create(
            type=Semester.TYPE_WINTER,
            year='2',
            semester_beginning=cls.current_semester.semester_ending +
            relativedelta(days=1),
            semester_ending=cls.current_semester.semester_ending +
            relativedelta(days=1, months=3),
            records_ects_limit_abolition=cls.current_semester.semester_ending +
            relativedelta(days=11),
            visible=True,
            is_grade_active=False)

        cls.next_summer_semester = Semester.objects.create(
            type=Semester.TYPE_SUMMER,
            year='3',
            semester_beginning=cls.next_winter_semester.semester_ending +
            relativedelta(days=1),
            semester_ending=cls.next_winter_semester.semester_ending +
            relativedelta(days=1, months=3),
            records_ects_limit_abolition=cls.next_winter_semester.
            semester_ending + relativedelta(days=11),
            visible=True,
            is_grade_active=False)

        cls.system_state = SystemState.objects.create(
            semester_winter=cls.next_winter_semester,
            semester_summer=cls.next_summer_semester,
            max_points=12,
            max_vote=3)

        cls.client = Client()

    @classmethod
    def tearDownTestData(cls) -> None:
        sql_calls = [
            'DROP TABLE courses_studentpointsview;',
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def test_new_semester_scenario(cls):
        cls.prepare_course_entities_for_voting()
        cls.perform_voting()
        cls.create_offer_for_winter_semester()
        cls.perform_winter_correction()
        # cls.import_winter_schedule()
        # cls.start_winter_semester()
        # cls.add_new_students()
        # cls.import_ects()
        # cls.open_records()
        # cls.generate_t0()

    def prepare_course_entities_for_voting(cls):
        #login as admin
        cls.client.post(
            "/fereol_admin/login/", {
                "username": cls.admin.username,
                "password": cls.password
            },
            follow=True)

        response = cls.client.get(
            "/offer/manage/select_for_voting", follow=True)

        #find all courses
        all_options = len(
            re.findall('(<option.*?\/option>)', str(response.content)))
        #find courses selected for voting
        selected_options = len(
            re.findall('(<option.*?selected="selected".*?\/option>)',
                       str(response.content)))
        
        #calculate nonselected courses
        nonselected_options = all_options - selected_options

        cls.assertEqual(
            CourseEntity.objects.filter(status=1).count(), nonselected_options)
        cls.assertEqual(
            CourseEntity.objects.filter(status=2).count(), selected_options)

        #Select courses for voting
        response = cls.client.post(
            "/offer/manage/select_for_voting",
            {'for_voting': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            follow=True)

        #find all courses
        all_options = len(
            re.findall('(<option.*?\/option>)', str(response.content)))
        
        #find courses selected for voting
        selected_options = len(
            re.findall('(<option.*?selected="selected".*?\/option>)',
                       str(response.content)))
        #calculate nonselected courses
        nonselected_options = all_options - selected_options

        cls.assertEqual(
            CourseEntity.objects.filter(status=1).count(), nonselected_options)
        cls.assertEqual(
            CourseEntity.objects.filter(status=2).count(), selected_options)

    def perform_voting(cls):
        # voting starts
        cls.system_state.vote_beg = date.today()
        cls.system_state.vote_end = date.today() + relativedelta(days=1)
        cls.system_state.save()

        cls.results_points = defaultdict(int)
        cls.results_votes = defaultdict(int)

        cls.vote(
            cls.student1, {
                'Course 1': 3,
                'Course 2': 3,
                'Course 3': 3,
                'Course 4': 3,
                'Course 5': 3,
                'Course 6': 3,
                'Course 7': 3,
                'Course 8': 3,
                'Course 9': 3,
                'Course 10': 3
            })
        cls.vote(
            cls.student1, {
                'Course 1': 1,
                'Course 2': 2,
                'Course 4': 3,
                'Course 5': 2,
                'Course 6': 2,
                'Course 7': 1,
                'Course 8': 1
            })
        cls.vote(
            cls.student2, {
                'Course 1': 2,
                'Course 2': 1,
                'Course 3': 3,
                'Course 4': 2,
                'Course 8': 1,
                'Course 9': 1,
                'Course 10': 2
            })
        cls.vote(
            cls.student3, {
                'Course 1': 3,
                'Course 3': 1,
                'Course 4': 2,
                'Course 6': 2,
                'Course 8': 2,
                'Course 10': 2
            })
        cls.vote(
            cls.student4, {
                'Course 2': 1,
                'Course 3': 2,
                'Course 5': 2,
                'Course 7': 3,
                'Course 8': 1,
                'Course 9': 1,
                'Course 10': 2
            })

        #Got to vote summary page
        response = cls.client.get("/vote/summary", follow=True)

        #Find table with courses body
        table_body = re.findall("<tbody>(.*?)<\/tbody>", str(response.content))
        table_body = "".join(table_body)

        #Find course rows in table
        rows = re.findall("<tr>(.*?)<\/tr>", str(table_body))

        #For each row in table
        for row in rows:
            #Extract course name
            name = re.findall("<a.*?>(.*?)<\/a>", str(row))[0]
            
            #Extract points and vote number for course
            points, votes = re.findall("<td class=\"number\">(.*?)</td>",
                                       str(row))

            cls.assertEqual(cls.results_points[name], int(points))
            cls.assertEqual(cls.results_votes[name], int(votes))
        
        #Close voting
        cls.system_state.vote_beg = date.today() - relativedelta(days=2)
        cls.system_state.vote_end = date.today() - relativedelta(days=1)
        cls.system_state.save()

    def vote(cls, student, points):
        
        #Logout user
        cls.client.get("/accounts/logout")

        #Login as student
        response = cls.client.post(
            "/users/login/", {
                "username": student.user.username,
                "password": cls.password
            },
            follow=True)

        #Go to voting page
        response = cls.client.get("/vote/vote", follow=True)

        #Find vote form body
        form_body = re.findall('(<div class="od-vote-semester".*<\/div>)',
                               str(response.content))[0]
        #Find all courses for voting
        vote_object = re.findall('(<input.*?<\/option><\/select><\/li>)',
                                 str(form_body))

        
        courses_for_vote = {}

        for course in vote_object:
            course_name = re.findall('<a.*?>(.*?)<\/a>', course)[0]
            form_course_name = re.findall('<input.*?name="(.*?)-id"',
                                          course)[0]
            id = re.findall('<input.*?value="(.*?)"', course)[0]
            courses_for_vote[course_name] = {"name": form_course_name, "id": id}


        request = {
            "winter-TOTAL_FORMS": "5",
            "winter-INITIAL_FORMS": "5",
            "winter-MIN_NUM_FORMS": "0",
            "winter-MAX_NUM_FORMS": "1000",
            "summer-TOTAL_FORMS": "5",
            "summer-INITIAL_FORMS": "5",
            "summer-MIN_NUM_FORMS": "0",
            "summer-MAX_NUM_FORM": "1000",
            "unknown-TOTAL_FORMS": "0",
            "unknown-INITIAL_FORMS": "0",
            "unknown-MIN_NUM_FORMS": "0",
            "unknown-MAX_NUM_FORMS": "1000"
        }
        
        #Create vote request
        for course_name in courses_for_vote:
            course = courses_for_vote[course_name]
            request["{}-id".format(course["name"])] = course["id"]
            request["{}-value".format(course["name"])] = points.get(
                course_name, 0)

        sum_points = sum(points.values())

        for course_name, value in points.items():
            if sum_points <= cls.system_state.max_points:
                cls.results_points[course_name] += value
                cls.results_votes[course_name] += 1

        response = cls.client.post("/vote/vote", request, follow=True)

        #Check vote succes
        succes_text = re.findall("alert-message succes", str(response.content))
        fail_text = re.findall("alert-message error", str(response.content))

        # alert-message error
        if sum_points <= cls.system_state.max_points:
            cls.assertTrue(succes_text)
        else:
            cls.assertTrue(fail_text)

    
    def create_offer_for_winter_semester(cls):
        for course in cls.winter_courses:
            Course.objects.create(
                entity=CourseEntity.objects.get(name=course),
                semester=cls.next_winter_semester
            )

    def perform_winter_correction(cls):
        # winter correction starts
        cls.system_state.winter_correction_beg = date.today()
        cls.system_state.winter_correction_end = date.today() + relativedelta(
            days=1)
        cls.system_state.save()

        cls.correction(
            cls.student1,
            {'Course 1': 3, 'Course 3': 3}
        )
        cls.correction(
            cls.student2,
            {'Course 2': 3}
        )
        cls.correction(
            cls.student3,
            {'Course 2': 2}
        )
        cls.correction(
            cls.student4,
            {'Course 1': 1, 'Course 2': 2}
        )

        # winter correction ends
        cls.system_state.winter_correction_beg = date.today() - relativedelta(
            days=2)
        cls.system_state.winter_correction_end = date.today() - relativedelta(
            days=1)
        cls.system_state.save()


    def correction(cls, student, points):
        
        #Logout user
        cls.client.get("/accounts/logout")

        #Login
        response = cls.client.post(
            "/users/login/", {
                "username": student.user.username,
                "password": cls.password
            },
            follow=True)
        
        #Go to voting page
        response = cls.client.get("/vote/vote", follow=True)

        form_body = re.findall('(<div class="od-vote-semester".*<\/div>)',
                               str(response.content))[0]
        vote_object = re.findall('(<input.*?<\/option><\/select><\/li>)',
                                 str(form_body))


        courses_for_vote = {}

        for course in vote_object:
            course_name = re.findall('<a.*?>(.*?)<\/a>', course)[0]
            form_course_name = re.findall('<input.*?name="(.*?)-id"',
                                          course)[0]
            id = re.findall('<input.*?value="(.*?)"', course)[0]
            old_value = re.findall("<option.*?selected>(.*?)<\/option>",course)[0]
            courses_for_vote[course_name] = {"name": form_course_name, "id": id,"old_value": old_value}

        request = {
            "winter-TOTAL_FORMS": "3",
            "winter-INITIAL_FORMS": "3",
            "winter-MIN_NUM_FORMS": "0",
            "winter-MAX_NUM_FORMS": "1000",
        }
        for course_name in courses_for_vote:
            course = courses_for_vote[course_name]
            request["{}-id".format(course["name"])] = course["id"]
            request["{}-value".format(course["name"])] = points.get(
                course_name, course["old_value"])

        response = cls.client.post("/vote/vote", request, follow=True)


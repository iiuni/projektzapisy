from django.test import TransactionTestCase

from django.contrib.auth.models import User
from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.courses.models.points import StudentPointsView
from apps.enrollment.records.utils import run_rearanged
from apps.users.models import Student, Employee
from django.db import connection
from apps.enrollment.courses.tests.factories import GroupFactory, \
    CourseFactory, SemesterFactory
from apps.users.tests.factories import StudentFactory
from apps.users.models import OpeningTimesView
from apps.enrollment.records.models import Record, Queue


from datetime import datetime, timedelta


def open_course_for_student(student, course, opening_time=datetime.now()):
    # OpeningTimesView has student as pk
    # so we cannot have more than one course opened at the moment
    otvs = OpeningTimesView.objects.filter(student=student)
    for otv in otvs:
        otv.delete()
    OpeningTimesView.objects.create(
        student=student,
        course=course,
        semester=course.semester,
        opening_time=opening_time)


def add_points_for_course(student, course):
    StudentPointsView.objects.create(student=student,
                                     value=course.entity.ects,
                                     entity=course.entity)


class DummyTest(TransactionTestCase):
    reset_sequences = True

    def createSemester(self):
        today = datetime.now()
        semester = Semester(
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
        semester.save()
        return semester

    def createStudentUser(self):
        user = User(
            username='jdz',
            first_name='Jan',
            last_name='Dzban',
            is_active=True)
        user.save()
        student = Student(
            matricula='221135',
            user=user)
        student.save()
        return user

    def createTeacher(self):
        user = User(
            username='klo',
            is_active=True)
        user.save()
        employee = Employee(user=user)
        employee.save()
        return (user, employee)

    def createCourse(self, semester):
        entity = CourseEntity(name="Algorytmy i Struktury Danych")
        entity.save()
        course = Course(
            lectures=30,
            exercises=30,
            laboratories=30,
            entity=entity,
            semester=semester,
            type=1,
            name="Algorytmy i Struktury Danych")
        course.save()
        return course

    def createExerciseGroup(self, course, teacher):
        group = Group(
            type=2,
            limit=5,
            course=course,
            teacher=teacher)
        group.save()
        return group

    def createLectureGroup(self, course, teacher):
        group = Group(
            type=1,
            limit=100,
            course=course,
            teacher=teacher)
        group.save()
        return group

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

    def tearDown(self):
        sql_calls = [
            "DROP TABLE courses_studentpointsview;",
        ]
        for sql_call in sql_calls:
            cursor = connection.cursor()
            cursor.execute(sql_call)
            connection.commit()

    def testAddStudentToGroup(self):
        today = datetime.now()
        group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        student = StudentFactory()
        open_course_for_student(student, group.course)
        result, messages_list = group.enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])

    def testAddingStudentToExercisesShouldAddItToLecture(self):
        today = datetime.now()
        course = CourseFactory()
        exercises_group = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        lecture_group = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
            type=1
        )
        student = StudentFactory()
        open_course_for_student(student, course)
        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list,
                         ['Student dopisany do grupy',
                          'Nastąpiło automatyczne dopisanie do grupy wykładowej'])
        self.assertTrue(Record.objects.filter(group_id=lecture_group.id, student_id=student.id,
                                              status=Record.STATUS_ENROLLED).exists())
        self.assertTrue(Record.objects.filter(group_id=exercises_group.id, student_id=student.id,
                                              status=Record.STATUS_ENROLLED).exists())

    def testAddingStudentToSameGroupAgainFails(self):
        today = datetime.now()
        exercises_group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        student = StudentFactory()
        open_course_for_student(student, exercises_group.course)

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        self.assertFalse(result)
        self.assertEqual(messages_list, ['Jesteś już w tej grupie'])

    def testAddingStudentToDifferentGroupsSameCourseSucceeds(self):
        today = datetime.now()
        course = CourseFactory()
        exercises_group1 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        exercises_group2 = GroupFactory(
            course=course,
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        student = StudentFactory()
        open_course_for_student(student, course)

        result, messages_list = exercises_group1.enroll_student(student)
        run_rearanged(result)

        result, messages_list = exercises_group2.enroll_student(student)
        run_rearanged(result)

        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])
        record_for_group1 = Record.objects.filter(
            student_id=student.id, group_id=exercises_group1.id)[0]
        record_for_group2 = Record.objects.filter(
            student_id=student.id, group_id=exercises_group2.id)[0]
        self.assertEqual(record_for_group1.status, Record.STATUS_REMOVED)
        self.assertEqual(record_for_group2.status, Record.STATUS_ENROLLED)

    def testEnrollmentFailsIfEnrollmentNotYetStarted(self):
        today = datetime.now()
        exercises_group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6)
        )
        student = StudentFactory()
        open_course_for_student(
            student,
            exercises_group.course,
            opening_time=today +
            timedelta(
                days=1))

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        self.assertFalse(result)
        self.assertEqual(messages_list, ['Zapisy na ten przedmiot są dla Ciebie zamknięte'])

    def testEnrollmentFailsIfEnrollmentHasEnded(self):
        today = datetime.now()
        exercises_group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-3),
            course__semester__records_closing=today + timedelta(days=-2)
        )
        student = StudentFactory()
        open_course_for_student(student, exercises_group.course)

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        self.assertFalse(result)
        self.assertEqual(
            messages_list,
            ['Zapisy na ten semestr zostały zakończone. Nie możesz dokonywać zmian.'])

    def testCannotLeaveGroupAfterRecordsEnded(self):
        today = datetime.now()
        exercises_group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-3),
            course__semester__records_closing=today + timedelta(days=6),
            course__semester__records_ending=today + timedelta(-2)
        )
        student = StudentFactory()
        open_course_for_student(student, exercises_group.course)

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        self.assertTrue(result)

        result, messages_list = exercises_group.remove_student(student)
        run_rearanged(result)

        self.assertFalse(result)
        self.assertEqual(
            messages_list,
            ['Wypisy w tym semestrze zostały zakończone. Nie możesz wypisać się z grupy.'])

    def testCanLeaveQueueAfterRecordsEnded(self):
        today = datetime.now()
        exercises_group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-3),
            course__semester__records_closing=today + timedelta(days=6),
            course__semester__records_ending=today + timedelta(-2)
        )

        students = StudentFactory.create_batch(10)
        for student in students:
            open_course_for_student(student, exercises_group.course)
            result, messages_list = exercises_group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, ['Student dopisany do grupy'])

        student = StudentFactory()
        open_course_for_student(student, exercises_group.course)

        result, messages_list = exercises_group.enroll_student(student)
        run_rearanged(result)

        self.assertTrue(result)

        result, messages_list = exercises_group.remove_student(student)
        run_rearanged(result)

        self.assertTrue(result)

    def testAddStudentToQueue(self):
        today = datetime.now()
        group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
        )
        students = StudentFactory.create_batch(15)
        for student in students:
            open_course_for_student(student, group.course)
        for student in students[:10]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, ['Student dopisany do grupy'])
        for student in students[10:]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, [
                'Brak wolnych miejsc w grupie',
                'Student został dopisany do kolejki'])
        self.assertEqual(group.enrolled, 10)
        self.assertEqual(group.queued, 5)

    def testIsQueueWorking(self):
        today = datetime.now()
        group = GroupFactory(
            course__semester__records_opening=today + timedelta(days=-1),
            course__semester__records_closing=today + timedelta(days=6),
        )
        students = StudentFactory.create_batch(15)
        for student in students:
            open_course_for_student(student, group.course)
        for student in students[:10]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result, group)
            self.assertTrue(result)
            self.assertEqual(messages_list, ['Student dopisany do grupy'])
        for student in students[10:]:
            result, messages_list = group.enroll_student(student)
            run_rearanged(result)
            self.assertTrue(result)
            self.assertEqual(messages_list, [
                'Brak wolnych miejsc w grupie',
                'Student został dopisany do kolejki'])
        self.assertEqual(group.enrolled, 10)
        self.assertEqual(group.queued, 5)
        result, messages_list = group.remove_student(students[8])
        run_rearanged(result, group)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student wypisany z grupy'])
        enrolled = [x.student for x in Record.objects.filter(
            group=group,
            status=Record.STATUS_ENROLLED)]
        removed = [x.student for x in Record.objects.filter(
            group=group,
            status=Record.STATUS_REMOVED)]
        queued = [x.student for x in
                  Queue.objects.filter(group=group, deleted=False)]
        should_be_enrolled = students[0:8] + students[9:11]
        should_be_queued = students[11:]
        should_be_removed = [students[8]]
        self.assertEqual(set(enrolled), set(should_be_enrolled))
        self.assertEqual(set(queued), set(should_be_queued))
        self.assertEqual(set(removed), set(should_be_removed))
        self.assertFalse(students[8] in enrolled)
        self.assertTrue(students[8] in removed)
        self.assertEqual(group.enrolled, 10)
        self.assertEqual(group.queued, 4)
        self.assertFalse(students[8] in queued)

    def testECTSLimit(self):
        today = datetime.now()
        semester = SemesterFactory(
            records_opening=today + timedelta(days=-1),
            records_closing=today + timedelta(days=6),
            records_ects_limit_abolition=today + timedelta(days=3),
        )
        groups = GroupFactory.create_batch(
            2,
            course__entity__ects=30,
            course__semester=semester)
        student = StudentFactory()
        for group in groups:
            add_points_for_course(student, group.course)
        open_course_for_student(student, groups[0].course)
        result, messages_list = groups[0].enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])
        open_course_for_student(student, groups[1].course)
        result, messages_list = groups[1].enroll_student(student)
        run_rearanged(result)
        self.assertFalse(result)
        self.assertEqual(messages_list,
                         ['Przekroczono limit 35 punktów. Zapis niemożliwy.'])

    def testECTSLimitAfterAbolition(self):
        today = datetime.now()
        semester = SemesterFactory(
            records_opening=today + timedelta(days=-3),
            records_closing=today + timedelta(days=6),
            records_ects_limit_abolition=today + timedelta(days=-1),
        )
        largeGroups = GroupFactory.create_batch(
            2,
            course__entity__ects=30,
            course__semester=semester)
        littleGroup = GroupFactory(
            course__entity__ects=15,
            course__semester=semester
        )
        student = StudentFactory()
        for group in largeGroups + [littleGroup]:
            add_points_for_course(student, group.course)
        open_course_for_student(student, largeGroups[0].course)
        result, messages_list = largeGroups[0].enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])
        open_course_for_student(student, largeGroups[1].course)
        result, messages_list = largeGroups[1].enroll_student(student)
        run_rearanged(result)
        self.assertFalse(result)
        self.assertEqual(messages_list,
                         ['Przekroczono limit 45 punktów. Zapis niemożliwy.'])
        open_course_for_student(student, littleGroup.course)
        result, messages_list = littleGroup.enroll_student(student)
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])

    def testQueuesWithECTSLimit(self):
        today = datetime.now()
        semester = SemesterFactory(
            records_opening=today + timedelta(days=-3),
            records_closing=today + timedelta(days=6),
            records_ects_limit_abolition=today + timedelta(days=1),
        )
        groups = GroupFactory.create_batch(
            3,
            course__entity__ects=15,
            course__semester=semester,
            limit=5)
        students = StudentFactory.create_batch(7)
        for student in students:
            for group in groups:
                add_points_for_course(student, group.course)
        for student in students[2:]:
            for group in groups[:2]:
                open_course_for_student(student, group.course)
                result, messages_list = group.enroll_student(student)
                run_rearanged(result)
                self.assertTrue(result)
                self.assertEqual(messages_list, ['Student dopisany do grupy'])
        open_course_for_student(students[0], groups[2].course)
        result, messages_list = groups[2].enroll_student(students[0])
        run_rearanged(result)
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student dopisany do grupy'])
        for group in groups[:2]:
            for student in students[:2]:
                open_course_for_student(student, group.course)
                result, messages_list = group.enroll_student(student)
                run_rearanged(result)
                self.assertTrue(result)
                self.assertEqual(messages_list, [
                    'Brak wolnych miejsc w grupie',
                    'Student został dopisany do kolejki'])
        result, messages_list = groups[0].remove_student(students[2])
        run_rearanged(result, groups[0])
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student wypisany z grupy'])
        self.assertEqual(groups[0].enrolled, 5)
        self.assertEqual(groups[0].queued, 1)
        enrolled = [x.student for x in Record.objects.filter(
            group=groups[0],
            status=Record.STATUS_ENROLLED)]
        removed = [x.student for x in Record.objects.filter(
            group=groups[0],
            status=Record.STATUS_REMOVED)]
        queued = [x.student for x in
                  Queue.objects.filter(group=groups[0], deleted=False)]
        should_be_enrolled = [students[0]] + students[3:]
        should_be_queued = [students[1]]
        should_be_removed = [students[2]]
        self.assertEqual(set(enrolled), set(should_be_enrolled))
        self.assertEqual(set(queued), set(should_be_queued))
        self.assertEqual(set(removed), set(should_be_removed))
        result, messages_list = groups[1].remove_student(students[2])
        run_rearanged(result, groups[1])
        self.assertTrue(result)
        self.assertEqual(messages_list, ['Student wypisany z grupy'])
        self.assertEqual(groups[1].enrolled, 5)
        self.assertEqual(groups[1].queued, 0)
        enrolled = [x.student for x in Record.objects.filter(
            group=groups[1],
            status=Record.STATUS_ENROLLED)]
        removed = [x.student for x in Record.objects.filter(
            group=groups[1],
            status=Record.STATUS_REMOVED)]
        queued = [x.student for x in
                  Queue.objects.filter(group=groups[1], deleted=False)]
        should_be_enrolled = [students[1]] + students[3:]
        should_be_queued = []
        should_be_removed = [students[2]]
        self.assertEqual(set(enrolled), set(should_be_enrolled))
        self.assertEqual(set(queued), set(should_be_queued))
        self.assertEqual(set(removed), set(should_be_removed))

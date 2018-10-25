from datetime import datetime, timedelta

from django.contrib.auth.models import User

from apps.enrollment.courses.models.group import Group
from apps.enrollment.courses.models.course import Course, CourseEntity
from apps.enrollment.courses.models.semester import Semester
from apps.users.models import Student, Employee


def create_semester():
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


def create_student_user():
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


def create_teacher():
    user = User(
        username='klo',
        is_active=True)
    user.save()
    employee = Employee(user=user)
    employee.save()
    return (user, employee)


def create_course(semester):
    entity = CourseEntity(name="Algorytmy i Struktury Danych")
    entity.save()
    course = Course(
        entity=entity,
        semester=semester)
    course.save()
    return course


def create_exercise_group(course, teacher):
    group = Group(
        type=2,
        limit=5,
        course=course,
        teacher=teacher)
    group.save()
    return group


def create_lecture_group(course, teacher):
    group = Group(
        type=1,
        limit=100,
        course=course,
        teacher=teacher)
    group.save()
    return group

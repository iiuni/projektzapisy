from datetime import datetime, time

import factory
from factory.django import DjangoModelFactory

from apps.common import days_of_week
from apps.users.tests.factories import EmployeeFactory

from ..models.classroom import Classroom
from ..models.course_information import CourseInformation
from ..models.course_instance import CourseInstance
from ..models.course_type import Type
from ..models.group import Group, GroupType
from ..models.semester import ChangedDay, Semester
from ..models.term import Term
from .semester_year_provider import SemesterYearProvider

factory.Faker.add_provider(SemesterYearProvider)


class SemesterFactory(DjangoModelFactory):
    class Meta:
        model = Semester
        exclude = ('raw_year', )

    visible = True
    type = factory.Iterator([Semester.TYPE_WINTER, Semester.TYPE_SUMMER])
    raw_year = factory.Faker('semester_year')
    year = factory.LazyAttribute(lambda sem: Semester.get_semester_year_from_raw_year(sem.raw_year))
    is_grade_active = False
    if type == Semester.TYPE_WINTER:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year, 9, 20))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year, 10, 31))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year, 10, 1))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 1, 31))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year, 10, 1))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 2, 22))
        records_ects_limit_abolition =  \
            factory.LazyAttribute(lambda x: datetime(x.raw_year - 1, 10, 1))
    else:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 2, 1))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 3, 15))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 2, 25))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 6, 15))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 2, 25))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year + 1, 9, 30))
        records_ects_limit_abolition = \
            factory.LazyAttribute(lambda x: datetime(x.raw_year, 3, 1))


class CourseTypeFactory(DjangoModelFactory):
    class Meta:
        model = Type


class CourseInformationFactory(DjangoModelFactory):
    class Meta:
        model = CourseInformation

    owner = factory.SubFactory(EmployeeFactory)
    course_type = factory.SubFactory(CourseTypeFactory)

    name = factory.Iterator(["Szydełkowanie", "Gotowanie", "Prasowanie", "Mycie naczyń", "Pranie"])


class CourseInstanceFactory(CourseInformationFactory):
    class Meta:
        model = CourseInstance

    semester = factory.SubFactory(SemesterFactory)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    course = factory.SubFactory(CourseInstanceFactory)
    type = GroupType.EXERCISES
    limit = 10
    teacher = factory.SubFactory(EmployeeFactory)


class ChangedDayForFridayFactory(DjangoModelFactory):
    class Meta:
        model = ChangedDay

    weekday = days_of_week.FRIDAY


class ClassroomFactory(DjangoModelFactory):
    class Meta:
        model = Classroom

    number = '25'
    can_reserve = True
    type = 0
    floor = 0


class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term

    dayOfWeek = '2'
    start_time = time(10, 00)
    end_time = time(12, 00)
    group = factory.SubFactory(GroupFactory)

    @factory.post_generation
    def classrooms(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for classroom in extracted:
                self.groups.add(classroom)

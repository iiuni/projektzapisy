# -*- coding: utf-8 -*-

from datetime import date, datetime

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from ..models.course import Course, CourseEntity
from ..models.group import Group
from ..models.semester import ChangedDay, Semester
from ..models.classroom import Classroom
from apps.users.tests.factories import EmployeeFactory
import common


class SemesterFactory(DjangoModelFactory):

    class Meta:
        model = Semester
        exclude = ('whole_year', )

    visible = True
    type = factory.Iterator([Semester.TYPE_WINTER, Semester.TYPE_SUMMER])
    whole_year = factory.fuzzy.FuzzyInteger(2017, 2030)
    year = \
        factory.LazyAttribute(lambda x: ("%s/%s" % (x.whole_year,
                                                    x.whole_year % 100 + 1)))
    is_grade_active = False
    if type == Semester.TYPE_WINTER:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 9, 20))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 31))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 1))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 1, 31))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 10, 1))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 22))
        records_ects_limit_abolition =  \
            factory.LazyAttribute(lambda x: datetime(x.whole_year-1, 10, 1))
    else:
        records_opening = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 1))
        records_closing = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 3, 15))
        lectures_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 25))
        lectures_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 6, 15))
        semester_beginning = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 2, 25))
        semester_ending = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year+1, 9, 30))
        records_ects_limit_abolition = \
            factory.LazyAttribute(lambda x: datetime(x.whole_year, 3, 1))


class CourseEntityFactory(DjangoModelFactory):

    class Meta:
        model = CourseEntity

    name = factory.Sequence(lambda n: 'course_entity_{0}'.format(n))
    ects = 5
    suggested_for_first_year = False


class CourseFactory(DjangoModelFactory):

    class Meta:
        model = Course

    lectures = 30
    exercises = 30
    laboratories = 30
    entity = factory.SubFactory(CourseEntityFactory)
    semester = factory.SubFactory(SemesterFactory)
    type = 1
    name = factory.Sequence(lambda n: 'course_{0}'.format(n))

class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    course = factory.SubFactory(CourseFactory)
    type = 2
    limit = 10
    teacher = factory.SubFactory(EmployeeFactory)


class ChangedDayForFridayFactory(DjangoModelFactory):
    class Meta:
        model = ChangedDay

    weekday = common.FRIDAY

class ClassroomFactory(DjangoModelFactory):
    class Meta:
        model = Classroom

    number = '25'
    can_reserve = True
    type = 0
    floor = 0

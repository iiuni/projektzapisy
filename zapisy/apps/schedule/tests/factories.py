# -*- coding: utf-8 -*-

from datetime import time, date, datetime
import string
import common
import random

import factory
import factory.fuzzy
from factory.django import DjangoModelFactory

from apps.users.tests.factories import UserFactory
from apps.enrollment.courses.models import Semester
from apps.enrollment.courses.tests.factories import GroupFactory, \
    SemesterFactory, ClassroomFactory
from apps.schedule.models import Event, Term, SpecialReservation


class EventCourseFactory(DjangoModelFactory):
    class Meta:
        model = Event

    visible = True
    group = factory.SubFactory(GroupFactory)
    author = factory.SubFactory(UserFactory)

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    type = factory.Iterator([
        Event.TYPE_GENERIC, Event.TYPE_CLASS, Event.TYPE_TEST, Event.TYPE_EXAM, Event.TYPE_CLASS,
        Event.TYPE_OTHER
    ])
    visible = True
    status = Event.STATUS_ACCEPTED
    author = factory.SubFactory(UserFactory)
    title = factory.fuzzy.FuzzyText(length=50, chars=string.letters)
    description = factory.fuzzy.FuzzyText(length=120, chars=string.letters)

    @factory.post_generation
    def interested(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.interested.add(user)


class PendingEventFactory(EventFactory):
    status = Event.STATUS_PENDING


class RejectedEventFactory(EventFactory):
    status = Event.STATUS_REJECTED


class EventInvisibleFactory(EventFactory):
    visible = False


class TermThisYearFactory(DjangoModelFactory):
    class Meta:
        model = Term

    event = factory.SubFactory(EventFactory)
    room = factory.SubFactory(ClassroomFactory)
    day = factory.fuzzy.FuzzyNaiveDateTime(datetime.now(), force_year=datetime.now().year)
    start = time(10)
    end = time(12)

class TermFactory(DjangoModelFactory):
    class Meta:
        model = Term

    event = factory.SubFactory(EventFactory)
    room = factory.SubFactory(ClassroomFactory)
    day = factory.fuzzy.FuzzyNaiveDateTime(datetime.now(), force_year=datetime.now().year)
    start = random.randint(9,15)
    end = random.randint(16,19)
    start = time(start)
    end = time(end)

class TermFixedDayFactory(TermThisYearFactory):
    day = date(2016, 5, 20)
    start = time(15)
    end = time(16)


class SpecialReservationFactory(DjangoModelFactory):
    class Meta:
        model = SpecialReservation

    title = factory.Sequence(lambda n: 'Special reservation %d' % n)
    classroom = factory.SubFactory(ClassroomFactory)
    dayOfWeek = common.FRIDAY
    start_time = time(10, 15)
    end_time = time(12)

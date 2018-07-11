import factory
from factory.django import DjangoModelFactory

from apps.enrollment.courses.tests.factories import GroupFactory
from apps.enrollment.records.models import Record
from apps.users.tests.factories import StudentFactory


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record

    group = factory.SubFactory(GroupFactory)
    student = factory.SubFactory(StudentFactory)
    status = factory.Iterator([status[0] for status in Record.RECORD_STATUS])

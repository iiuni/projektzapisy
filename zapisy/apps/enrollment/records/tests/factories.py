import factory
from factory.django import DjangoModelFactory

from apps.enrollment.courses.tests.factories import GroupFactory
from apps.users.tests.factories import StudentFactory

from ..models.records import Record, RecordStatus


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record

    group = factory.SubFactory(GroupFactory)
    student = factory.SubFactory(StudentFactory)
    status = RecordStatus.ENROLLED

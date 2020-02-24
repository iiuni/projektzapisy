import factory
from factory.django import DjangoModelFactory

from ..models.records import Record, RecordStatus
from apps.users.tests.factories import StudentFactory
from apps.enrollment.courses.tests.factories import GroupFactory


class RecordFactory(DjangoModelFactory):
    class Meta:
        model = Record

    group = factory.SubFactory(GroupFactory)
    student = factory.SubFactory(StudentFactory)
    status = RecordStatus.ENROLLED

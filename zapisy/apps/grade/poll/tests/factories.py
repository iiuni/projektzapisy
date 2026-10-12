import random

import factory
from factory.django import DjangoModelFactory

from ..models import Submission


class SubmissionFactory(DjangoModelFactory):
    class Meta:
        model = Submission

    ticket = factory.Sequence(lambda n: random.randint(0, 1000000000) + n)
    submitted = True
    answers = factory.LazyAttribute(lambda sub: sub.schema.get_schema_with_random_answers())

from django.test import TestCase

from ..models import Program, Student
from . import factories


class SignalsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.p1 = Program.objects.create(name='licencjackie')
        cls.p2 = Program.objects.create(name='magisterskie')

    def test_new_student(self):
        s: Student = factories.StudentFactory(program=self.p1)
        self.assertTrue(s.user.groups.filter(name=self.p1.name).exists())

    def test_remove_program(self):
        s: Student = factories.StudentFactory(program=self.p1)
        self.assertTrue(s.user.groups.filter(name=self.p1.name).exists())
        s.program = None
        s.save()
        self.assertFalse(s.user.groups.filter(name=self.p1.name).exists())

    def test_change_program(self):
        s: Student = factories.StudentFactory(program=self.p1)
        self.assertTrue(s.user.groups.filter(name=self.p1.name).exists())
        s.program = self.p2
        s.save()
        self.assertFalse(s.user.groups.filter(name=self.p1.name).exists())
        self.assertTrue(s.user.groups.filter(name=self.p2.name).exists())

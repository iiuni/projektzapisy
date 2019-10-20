from typing import Any
from django.contrib.auth.models import Group
import factory
from factory.django import DjangoModelFactory
from factory import post_generation

from django.conf import settings

from apps.users.models import Student, Employee, User

langs = [x[0] for x in settings.LANGUAGES]


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        # factory is pretty stupid, and will not remember if
        # user was created for other factory
        exclude = ("pref_username", "suff_username", )

    pref_username = factory.Sequence(lambda n: 'testuser_{0}'.format(n))
    suff_username = ""
    username = factory.LazyAttribute(lambda o: o.pref_username + o.suff_username)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    first_name = 'user'
    last_name = factory.LazyAttributeSequence(lambda o, n: f'{n}{o.suff_username}')
    is_staff = False
    is_superuser = False
    email = factory.LazyAttribute(lambda o: o.pref_username + o.suff_username + '@example.com')


class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student
        exclude = ("group",)

    @post_generation
    def group(self, create: Any, extracted: Any, **kwargs: Any) -> Group:
        """Method taking care of checking whether user was added to students group."""
        students, _ = Group.objects.get_or_create(name='students')
        students.user_set.add(self.user)
        students.save()
        return students

    user = factory.SubFactory(UserFactory, suff_username="_s")
    matricula = factory.Sequence(lambda n: ('9%05d' % n))


class EmployeeFactory(DjangoModelFactory):
    class Meta:
        model = Employee
        exclude = ("group",)

    @post_generation
    def group(self, create: Any, extracted: Any, **kwargs: Any) -> Group:
        """Method taking care of checking whether user was added to employees group."""
        employees, _ = Group.objects.get_or_create(name='employees')
        employees.user_set.add(self.user)
        employees.save()
        return employees

    user = factory.SubFactory(UserFactory, suff_username="_e")

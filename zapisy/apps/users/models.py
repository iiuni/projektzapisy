import datetime
import logging
from typing import List, TYPE_CHECKING, Optional

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import QuerySet
from django.core.validators import MaxLengthValidator

from apps.users.exceptions import NonUserException

logger = logging.getLogger()

EMPLOYEE_STATUS_CHOICES = [(0, 'aktywny'), (1, 'nieaktywny')]
ISIM_PROGRAM_NAME = 'ISIM, dzienne I stopnia'


class Related(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super(Related, self).get_queryset().select_related('user')


def is_user_in_group(user: User, group_name: str) -> bool:
    return user.groups.filter(name=group_name).exists() if user else False


class BaseUser(models.Model):
    """
    User abstract class. For every app user there is entry in django.auth.
    We do not inherit after User directly, because of problems with logging beckend etc.
    """
    last_news_view = models.DateTimeField(default=datetime.datetime.now)

    objects = Related()

    def get_full_name(self) -> str:
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'

    def get_number_of_news(self) -> int:
        from apps.news.models import News
        if not hasattr(self, '_count_news'):
            self._count_news = News.objects.exclude(
                category='-').filter(date__gte=self.last_news_view).count()

        return self._count_news

    @staticmethod
    def get(user_id: int) -> User:
        """Returns user with specified id.

        Raises:
            NonUserException: If user with specified id doesn't exist.
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(
                'Getter(user_id = %d) in BaseUser throws User.DoesNotExist exception.' %
                user_id)
            raise NonUserException
        return user

    @staticmethod
    def is_student(user: User) -> bool:
        return is_user_in_group(user, 'students')

    @staticmethod
    def is_employee(user: User) -> bool:
        return is_user_in_group(user, 'employees')

    @staticmethod
    def is_external_contractor(user: User) -> bool:
        return is_user_in_group(user, 'external_contractors')

    def __str__(self) -> str:
        return self.get_full_name()

    class Meta:
        abstract: bool = True


class Employee(BaseUser):

    user = models.OneToOneField(
        User,
        verbose_name="Użytkownik",
        related_name='employee',
        on_delete=models.CASCADE)
    consultations = models.TextField(verbose_name="konsultacje", null=True, blank=True, validators=[MaxLengthValidator(4200)])
    homepage = models.URLField(verbose_name='strona domowa', default="", null=True, blank=True)
    room = models.CharField(max_length=20, verbose_name="pokój", null=True, blank=True)
    status = models.PositiveIntegerField(
        default=0,
        choices=EMPLOYEE_STATUS_CHOICES,
        verbose_name="Status")
    title = models.CharField(max_length=20, verbose_name="tytuł naukowy", null=True, blank=True)
    usos_id = models.PositiveIntegerField(verbose_name="ID w USOSie", null=True, blank=True)

    def has_privileges_for_group(self, group_id: int) -> bool:
        """
        Method used to verify whether user is allowed to create a poll for certain group
        (== he is an admin, a teacher for this course or a teacher for this group)
        """
        from apps.enrollment.courses.models.group import Group

        try:
            group = Group.objects.get(pk=group_id)
            return group.teacher == self or group.course.owner == self or self.user.is_staff
        except Group.DoesNotExist:
            logger.error(
                'Function Employee.has_privileges_for_group(group_id = %d) throws Group.DoesNotExist exception.' %
                group_id)
        return False

    @staticmethod
    def get_actives() -> QuerySet:
        return Employee.objects.filter(user__is_active=True).order_by('user__last_name',
                                                                      'user__first_name')

    @staticmethod
    def get_list(begin: str ='All') -> QuerySet:
        def next_char(begin: str) -> str:
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)
        if begin == 'Z':
            employees = Employee.objects.filter(user__last_name__gte=begin, status=0).\
                select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            employees = Employee.objects.filter(status=0).\
                select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            employees = Employee.objects.filter(user__last_name__range=(begin, end), status=0). \
                select_related().order_by('user__last_name', 'user__first_name')

        return employees

    class Meta:
        verbose_name = 'pracownik'
        verbose_name_plural = 'Pracownicy'
        app_label = 'users'
        ordering = ['user__last_name', 'user__first_name']
        permissions = (
            ("mailto_all_students", "Może wysyłać maile do wszystkich studentów"),
        )

    def get_full_name_with_academic_title(self) -> str:
        """Same as `get_full_name`, but prepends the employee's academic title
        if one is defined.
        """
        base_name = super().get_full_name()
        return f'{self.title} {base_name}' if self.title else base_name


class Student(BaseUser):

    user = models.OneToOneField(
        User,
        verbose_name="Użytkownik",
        related_name='student',
        on_delete=models.CASCADE)
    matricula = models.CharField(
        max_length=20,
        default="",
        unique=True,
        verbose_name="Numer indeksu")
    ects = models.PositiveIntegerField(verbose_name="punkty ECTS", default=0)
    records_opening_bonus_minutes = models.PositiveIntegerField(
        default=0, verbose_name="Przyspieszenie otwarcia zapisów (minuty)")
    program = models.ForeignKey(
        'Program',
        verbose_name='Program Studiów',
        null=True,
        default=None,
        on_delete=models.CASCADE)
    block = models.BooleanField(verbose_name="blokada planu", default=False)
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")
    status = models.PositiveIntegerField(default=0, verbose_name="Status")
    status.help_text = "0 - aktywny student, 1 - skreślony student"

    t0 = models.DateTimeField(null=True, blank=True)

    ects_in_semester = models.SmallIntegerField(default=0)

    dyskretna_l = models.BooleanField(default=False)
    numeryczna_l = models.BooleanField(default=False)
    algorytmy_l = models.BooleanField(default=False)
    programowanie_l = models.BooleanField(default=False)

    usos_id = models.PositiveIntegerField(
        null=True, blank=True, unique=True, verbose_name='Kod studenta w systemie USOS')

    def is_active(self) -> bool:
        return self.status == 0

    def is_isim(self) -> bool:
        try:
            return self.program == Program.objects.get(name=ISIM_PROGRAM_NAME)
        except Program.DoesNotExist:
            return False

    def consent_answered(self) -> bool:
        return hasattr(self, 'consent')

    def consent_granted(self) -> bool:
        return self.consent_answered() and self.consent.granted

    def get_type_of_studies(self) -> str:
        """Returns type of studies."""
        semestr = {
            1: 'pierwszy',
            2: 'drugi',
            3: 'trzeci',
            4: 'czwarty',
            5: 'piąty',
            6: 'szósty',
            7: 'siódmy',
            8: 'ósmy',
            9: 'dziewiąty',
            10: 'dziesiąty',
            0: 'niezdefiniowany'}[
            self.semestr]
        return '%s, semestr %s' % (self.program, semestr)
    get_type_of_studies.short_description = 'Studia'

    def participated_in_last_grades(self) -> int:
        from apps.grade.ticket_create.models.student_graded import StudentGraded
        return StudentGraded.objects.filter(student=self, semester__in=[45, 239]).count()

    @classmethod
    def get_active_students(cls) -> QuerySet:
        return cls.objects.filter(status=0)

    @staticmethod
    def get_list(begin: str='All', restrict_list_consent: Optional[bool]=True) -> QuerySet:
        def next_char(begin: str) -> str:
            try:
                return chr(ord(begin) + 1)
            except ValueError:
                return chr(90)

        qs = Student.objects.filter(status=0)
        if restrict_list_consent:
            qs = qs.filter(consent__granted=True)
        if begin == 'Z':
            return qs.filter(user__last_name__gte=begin).\
                select_related().order_by('user__last_name', 'user__first_name')
        elif begin == 'All':
            return qs.select_related().order_by('user__last_name', 'user__first_name')
        else:
            end = next_char(begin)
            return qs.filter(user__last_name__range=(begin, end)).\
                select_related().order_by('user__last_name', 'user__first_name')

    def records_set_locked(self, locked: bool) -> None:
        self.block = locked
        self.save()

    def is_first_year_student(self) -> bool:
        return (self.semestr in [1, 2]) and (self.program.id in [0, 2])

    class Meta:
        verbose_name: str = 'student'
        verbose_name_plural: str = 'studenci'
        app_label: str = 'users'
        ordering: List[str] = ['user__last_name', 'user__first_name']


class Program(models.Model):
    """
        Program of student studies
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Program")

    class Meta:
        verbose_name: str = 'Program studiów'
        verbose_name_plural: str = 'Programy studiów'

    def __str__(self) -> str:
        return self.name


class PersonalDataConsent(models.Model):
    """
        Model przechowuje zgody dotyczące udostępniania danych osobowych studentów
    """
    student = models.OneToOneField(Student, related_name='consent', on_delete=models.CASCADE)
    granted = models.NullBooleanField(verbose_name="zgoda udzielona")

    class Meta:
        verbose_name = 'Zgoda na udostępnianie danych osobowych'
        verbose_name_plural = 'Zgody na udostępnianie danych osobowych'

    def __str__(self):
        return f"{self.student.get_full_name()}: {self.granted}"

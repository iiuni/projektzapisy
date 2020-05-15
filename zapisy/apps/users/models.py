from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import QuerySet


def is_student(user: User) -> bool:
    return hasattr(user, 'student_ptr')


def is_employee(user: User) -> bool:
    return hasattr(user, 'employee_ptr')


def is_external_contractor(user: User) -> bool:
    return is_user_in_group(user, 'external_contractors')


def is_user_in_group(user: User, group_name: str) -> bool:
    return user.groups.filter(name=group_name).exists() if user else False


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name="Użytkownik",
        related_name='employee_ptr',
        related_query_name='employee',
        on_delete=models.CASCADE)
    consultations = models.TextField(verbose_name="konsultacje",
                                     null=True,
                                     blank=True,
                                     validators=[MaxLengthValidator(4200)])
    homepage = models.URLField(verbose_name='strona domowa', default="", null=True, blank=True)
    room = models.CharField(max_length=20, verbose_name="pokój", null=True, blank=True)
    title = models.CharField(max_length=20, verbose_name="tytuł naukowy", null=True, blank=True)
    usos_id = models.PositiveIntegerField(verbose_name="ID w USOSie", null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    def get_full_name(self) -> str:
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'

    @staticmethod
    def get_actives() -> QuerySet:
        return Employee.objects.filter(user__is_active=True).order_by('user__last_name',
                                                                      'user__first_name')

    class Meta:
        verbose_name = 'pracownik'
        verbose_name_plural = 'Pracownicy'
        app_label = 'users'
        ordering = ['user__last_name', 'user__first_name']
        permissions = (
            ("mailto_all_students", "Może wysyłać maile do wszystkich studentów"),
        )

    def get_full_name_with_academic_title(self) -> str:
        """Prepends the employee's academic title (if specified) to the name."""
        base_name = self.get_full_name()
        return f'{self.title} {base_name}' if self.title else base_name


class Student(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name="Użytkownik",
        related_name='student_ptr',
        related_query_name='student',
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
    semestr = models.PositiveIntegerField(default=0, verbose_name="Semestr")
    is_active = models.BooleanField("aktywny",
                                    default=True,
                                    help_text="Student może być aktywny lub skreślony.")

    usos_id = models.PositiveIntegerField(
        null=True, blank=True, unique=True, verbose_name='Kod studenta w systemie USOS')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricula})"

    def consent_answered(self) -> bool:
        return hasattr(self, 'consent')

    def consent_granted(self) -> bool:
        return self.consent_answered() and self.consent.granted

    def get_full_name(self) -> str:
        return self.user.get_full_name()
    get_full_name.short_description = 'Użytkownik'

    @classmethod
    def get_active_students(cls) -> QuerySet:
        return cls.objects.filter(is_active=True)

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'studenci'
        app_label = 'users'
        ordering = ['user__last_name', 'user__first_name']


class Program(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Program")

    class Meta:
        verbose_name: str = 'Program studiów'
        verbose_name_plural: str = 'Programy studiów'

    def __str__(self) -> str:
        return self.name


class PersonalDataConsent(models.Model):
    """Stores students' data processing consents."""
    student = models.OneToOneField(Student, related_name='consent', on_delete=models.CASCADE)
    granted = models.NullBooleanField(verbose_name="zgoda udzielona")

    class Meta:
        verbose_name = 'Zgoda na udostępnianie danych osobowych'
        verbose_name_plural = 'Zgody na udostępnianie danych osobowych'

    def __str__(self):
        return f"{self.student.get_full_name()}: {self.granted}"

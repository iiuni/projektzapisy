"""A model representing a single course group.

A group may have multiple terms - that is, students may meet with the teacher
more than one time a week.
"""
from django.db import models, transaction
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.notifications.custom_signals import teacher_changed
from apps.users.models import Employee


class GroupType(models.IntegerChoices):
    LECTURE = 1, 'wykład'
    EXERCISES = 2, 'ćwiczenia'
    LAB = 3, 'pracownia'
    EXERCISES_LAB = 5, 'ćwiczenio-pracownia'
    SEMINAR = 6, 'seminarium'
    LANGUAGE_COURSE = 7, 'lektorat'
    PE = 8, 'WF'
    COMPENDIUM = 9, 'repetytorium'
    PROJECT = 10, 'projekt'
    TUTORING = 11, 'tutoring'
    PRO_SEMINAR = 12, 'proseminarium'


GroupTooltips = {
    'Q1': "pierwsze 7 tygodni",
    'Q2': "drugie 7 tygodni",
    'zaaw': "grupa zaawansowana",
    'mat': "zajęcia na matematyce",
    'english': "grupa anglojęzyczna",
    'zdalna': "zajęcia prowadzone zdalnie",
    'hybrydowa': "zajęcia częściowo zdalne, częściowo stacjonarne",
}


class Group(models.Model):
    course = models.ForeignKey(
        CourseInstance,
        verbose_name='przedmiot',
        related_name='groups',
        on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        verbose_name='prowadzący',
        on_delete=models.CASCADE)
    type = models.IntegerField(choices=GroupType.choices, verbose_name='typ zajęć')
    limit = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    auto_enrollment = models.BooleanField(
        "grupa z auto-zapisem",
        default=False,
        help_text=(
            "Blokuje zapisywanie do grupy. Zamiast tego, studenci są do niej automatycznie "
            "zapisani jeśli zapiszą się do jakiejkolwiek innej grupy z tego przedmiotu. "
            "Nie należy blokować wszystkich grup z przedmiotu ani grup, gdzie studenci powinni "
            "mieć wybór (np. jest kilka równoległych grup ćwiczeniowych)."))
    extra = models.CharField(
        "dodatkowe informacje",
        max_length=255,
        default='',
        blank=True,
        help_text=("Można wpisywać tagi oddzielone przecinkami. Zostaną one wyświetlone na stronie "
                   "przedmiotu. Nie ma żadnych dozwolonych tagów, ale dla wybranych tagów zostanie "
                   f"dodany tooltip z wyjaśnieniem: {GroupTooltips}"))
    export_usos = models.BooleanField(default=True, verbose_name='czy eksportować do usos?')
    usos_nr = models.IntegerField("Nr grupy w usos", null=True, blank=True)

    def get_teacher_full_name(self):
        """Return teacher's full name for current group."""
        if self.teacher is None:
            return '(nieznany prowadzący)'
        else:
            return self.teacher.user.get_full_name()

    def get_all_terms(self):
        """Return all terms of current group."""
        return self.term.all()

    def get_terms_as_string(self):
        return ",".join(["%s %s-%s" % (x.get_dayOfWeek_display(),
                                       x.start_time.hour, x.end_time.hour) for x in self.term.all()])
    get_terms_as_string.short_description = 'Terminy zajęć'

    @staticmethod
    def teacher_in_present(employees, semester):
        teachers = Group.objects.filter(
            course__semester=semester).distinct().values_list(
            'teacher__pk', flat=True)

        for employee in employees:
            employee.teacher = employee.pk in teachers

        return employees

    class Meta:
        verbose_name = 'grupa'
        verbose_name_plural = 'grupy'
        app_label = 'courses'

    def __str__(self):
        return "%s: %s - %s" % (str(self.course.get_short_name()),
                                str(self.get_type_display()),
                                str(self.get_teacher_full_name()))

    def long_print(self):
        return "%s: %s - %s" % (str(self.course.name),
                                str(self.get_type_display()),
                                str(self.get_teacher_full_name()))

    def get_absolute_url(self):
        return reverse('group-view', args=[self.pk])

    def get_extra_tags(self):
        return [(k, GroupTooltips.get(k, None)) for k in self.extra.split(',')]

    @classmethod
    @transaction.atomic
    def copy(cls, group: 'Group') -> 'Group':
        """Creates a copy of the group.

        All the fields in the copy are left the same. The terms and their
        classrooms are copied.

        This function is operating inside a transaction. If it fails, no changes
        are made to the DB.
        """
        from apps.enrollment.courses.models.term import Term
        from apps.schedulersync.models import TermSyncData

        def copy_term(t: Term) -> Term:
            classrooms = list(t.classrooms.all())
            term_sync_data: TermSyncData = list(t.termsyncdata_set.all())
            t.pk = None
            t.save()
            t.classrooms.set(classrooms)
            for tsd in term_sync_data:
                tsd.pk = None
                tsd.term = t
                tsd.save()
            return t

        copied_terms = [copy_term(t) for t in group.term.all()]
        copy = cls.objects.get(pk=group.pk)
        copy.pk = None
        copy.save()
        copy.term.set(copied_terms)
        return copy

    def save(self, *args, **kwargs):
        """Overloaded save method.

        During save check changes and send signals to notifications app.
        """
        old = type(self).objects.get(pk=self.pk) if self.pk else None
        super(Group, self).save(*args, **kwargs)
        if old:
            if old.teacher != self.teacher:
                teacher_changed.send(sender=self.__class__, instance=self, teacher=self.teacher)


class GuaranteedSpotsManager(models.Manager):
    """This thin manager always pulls auth.Group names for efficiency."""
    def get_queryset(self):
        return super().get_queryset().select_related('role')


class GuaranteedSpots(models.Model):
    """Defines an additional pool of spots in a course group reserved for a role.

    Normally a course group would have a single limit defining how many students
    can be enrolled to it at the same time. Sometimes we would however like to
    reserve a number of spots to a group of students (i.e. freshmen, or ISIM).
    This mechanism will allow us to do that.
    """
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='guaranteed_spots',
        verbose_name="grupa zajęciowa")
    role = models.ForeignKey(
        'auth.Group', on_delete=models.CASCADE, related_name='+', verbose_name='grupa użytkowników')
    limit = models.PositiveSmallIntegerField("liczba miejsc")

    objects = GuaranteedSpotsManager()

    class Meta:
        verbose_name = 'miejsca gwarantowane'
        verbose_name_plural = 'miejsca gwarantowane'

    def __str__(self):
        return f"{self.limit} miejsc gwarantowanych w grupie {self.group} dla użytkowników {self.role}"

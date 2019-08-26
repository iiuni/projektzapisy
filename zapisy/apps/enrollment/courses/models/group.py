"""A model representing a single course group.

A group may have multiple terms - that is, students may meet with the teacher
more than one time a week.
"""
from typing import Optional

from django.db import models, transaction
from django.urls import reverse

from apps.enrollment.courses.models.course_instance import CourseInstance
from apps.notifications.custom_signals import teacher_changed
from apps.users.models import Employee


# w przypadku edycji, poprawić też javascript: Fereol.Enrollment.CourseGroup.groupTypes
GROUP_TYPE_CHOICES = [('1', 'wykład'), ('2', 'ćwiczenia'), ('3', 'pracownia'),
                      ('5', 'ćwiczenio-pracownia'),
                      ('6', 'seminarium'), ('7', 'lektorat'), ('8', 'WF'),
                      ('9', 'repetytorium'), ('10', 'projekt'),
                      ('11', 'tutoring'), ('12', 'proseminarium')]

GROUP_EXTRA_CHOICES = [('', ''),
                       ("pierwsze 7 tygodni", "pierwsze 7 tygodni"),
                       ("drugie 7 tygodni", "drugie 7 tygodni"),
                       ('grupa rezerwowa', 'grupa rezerwowa'),
                       ('grupa licencjacka', 'grupa licencjacka'),
                       ('grupa magisterska', 'grupa magisterska'),
                       ('grupa zaawansowana', 'grupa zaawansowana'),
                       ('zajecia na mat.', 'zajęcia na matematyce'),
                       ('wykład okrojony', 'wykład okrojony'),
                       ('grupa 1', 'grupa 1'),
                       ('grupa 2', 'grupa 2'),
                       ('grupa 3', 'grupa 3'),
                       ('grupa 4', 'grupa 4'),
                       ('grupa 5', 'grupa 5'),
                       ('pracownia linuksowa', 'pracownia linuksowa'),
                       ('grupa anglojęzyczna', 'grupa anglojęzyczna'),
                       ('I rok', 'I rok'), ('II rok', 'II rok'), ('ISIM', 'ISIM'),
                       ('hidden', 'grupa ukryta'),
                       ]


class Group(models.Model):
    """group for course"""
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
    type = models.CharField(max_length=2, choices=GROUP_TYPE_CHOICES, verbose_name='typ zajęć')
    GROUP_TYPE_LECTURE = '1'
    limit = models.PositiveSmallIntegerField(default=0, verbose_name='limit miejsc')
    extra = models.CharField(
        max_length=20,
        choices=GROUP_EXTRA_CHOICES,
        verbose_name='dodatkowe informacje',
        default='',
        blank=True)
    export_usos = models.BooleanField(default=True, verbose_name='czy eksportować do usos?')

    disable_update_signal = False

    usos_nr = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nr grupy w usos',
        help_text='UWAGA! Nie edytuj tego pola sam!')

    def get_teacher_full_name(self):
        """return teacher's full name of current group"""
        if self.teacher is None:
            return '(nieznany prowadzący)'
        else:
            return self.teacher.user.get_full_name()

    def get_all_terms(self):
        """return all terms of current group"""
        return self.term.all()

    def get_all_terms_for_export(self):
        """return all terms of current group"""
        from apps.schedule.models.term import Term
        return Term.objects.filter(event__group=self)

    def human_readable_type(self):
        types = {
            '1': 'Wykład',
            '9': 'Repetytorium',
            '2': 'Ćwiczenia',
            '3': 'Pracownia',
            '4': 'Ćwiczenia (poziom zaawansowany)',
            '5': 'Ćwiczenio-pracownia',
            '6': 'Seminarium',
            '7': 'Lektorat',
            '8': 'Zajęcia sportowe',
            '10': 'Projekt',
        }
        return types[str(self.type)]

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

    @classmethod
    def get_lecture_group(cls, course_id: int) -> Optional['Group']:
        """Given a course_id returns a lecture group for this course, if one exists.

        The Group.MultipleObjectsReturned exception will be raised when many
        lecture groups exist for course.
        """
        group_query = cls.objects.filter(course_id=course_id, type=Group.GROUP_TYPE_LECTURE)
        try:
            return group_query.get()
        except cls.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """Overloaded save method - during save check changes and send signals to notifications app"""
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

from datetime import date
import datetime
from typing import Optional

from django.core.cache import cache as mcache
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify

from apps.cache_utils import cache_result, cache_result_for
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.student_options import StudentOptions
from apps.enrollment.courses.models.tag import Tag
from apps.users.models import Student

import logging

logger = logging.getLogger()


class WithInformation(models.Manager):
    """ Manager for course objects with visible semester """

    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(WithInformation, self).get_queryset().select_related('information')


class NoRemoved(WithInformation):
    """ Manager for course objects with visible semester """

    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(NoRemoved, self).get_queryset().filter(deleted=False, owner__isnull=False)


class SimpleManager(models.Manager):
    def get_with_opening(self, student):
        return self.ex


class DefaultCourseManager(models.Manager):
    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(
            DefaultCourseManager,
            self).get_queryset().select_related(
            'entity',
            'information')


class StatisticsManager(models.Manager):
    def in_year(self, year=None):
        from apps.offer.vote.models import SystemState

        if not year:
            year = date.today().year

        state = SystemState.get_state(year)

        # TODO: po przeniesieniu wszystkich metod do managerów filtrowanie na
        #  status powinno byc  z dziedziczenia
        return self.get_queryset().filter(
            status=2) .select_related(
            'type',
            'owner',
            'owner__user') .order_by('name') .extra(
            select={
                'votes': "COALESCE((SELECT SUM(vote_singlevote.correction) FROM vote_singlevote WHERE"
                " vote_singlevote.entity_id = courses_courseentity.id"
                " AND vote_singlevote.state_id = %d), 0)" %
                state.id,
                'voters': "SELECT COUNT(*) FROM vote_singlevote WHERE"
                " vote_singlevote.entity_id = courses_courseentity.id "
                "AND vote_singlevote.correction > 0 "
                "AND vote_singlevote.state_id = %d" %
                state.id,
                'maxpoints_votes': "COALESCE((SELECT SUM(vote_singlevote.correction) FROM vote_singlevote WHERE"
                " vote_singlevote.correction = 3 "
                " AND vote_singlevote.entity_id = courses_courseentity.id"
                " AND vote_singlevote.state_id = %d), 0)" %
                state.id,
                'maxpoints_voters': "SELECT COUNT(*) FROM vote_singlevote WHERE"
                " vote_singlevote.entity_id = courses_courseentity.id "
                "AND vote_singlevote.correction = 3 "
                "AND vote_singlevote.state_id = %d" %
                state.id})


semesters = (('u', 'nieoznaczony'), ('z', 'zimowy'), ('l', 'letni'))
ectslist = [(x, str(x)) for x in range(1, 16)]


class CourseEntity(models.Model):
    """entity of particular course title"""

    information = models.ForeignKey(
        'CourseDescription',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    # Test name
    name = models.CharField(max_length=100,
                            verbose_name='nazwa')
    shortName = models.CharField(
        max_length=30,
        verbose_name='skrócona nazwa',
        null=True,
        blank=True,
        help_text='Opcjonalna skrócona nazwa, używana na np. planie. Przykłady: JFiZO, AiSD')

    STATUS_PROPOSITION = 0
    STATUS_IN_OFFER = 1
    STATUS_TO_VOTE = 2
    STATUS_WITHDRAWN = 4
    STATUS_FOR_REVIEW = 5

    STATUS_CHOICES = [(STATUS_PROPOSITION, 'Propozycja'),
                      (STATUS_IN_OFFER, 'W ofercie'),
                      (STATUS_TO_VOTE, 'Poddana pod głosowanie'),
                      (STATUS_WITHDRAWN, 'Wycofany z oferty'),
                      (STATUS_FOR_REVIEW, 'Do poprawienia')]

    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_PROPOSITION)

    semester = models.CharField(
        max_length=1,
        choices=semesters,
        default='u',
        verbose_name='semestr')

    type = models.ForeignKey('Type', on_delete=models.CASCADE,
                             verbose_name='rodzaj',
                             null=True)
    english = models.BooleanField(default=False,
                                  verbose_name='przedmiot prowadzony w j.angielskim')
    exam = models.BooleanField(verbose_name='egzamin',
                               default=True)

    suggested_for_first_year = models.BooleanField(
        verbose_name='polecany dla pierwszego roku', default=False)

    web_page = models.URLField(verbose_name='strona www', null=True, blank=True)
    ects = models.IntegerField(null=True, blank=True)
    lectures = models.IntegerField(null=True, blank=True, verbose_name='godzin wykładu')
    exercises = models.IntegerField(null=True, blank=True, verbose_name='godzin ćwiczeń')
    laboratories = models.IntegerField(null=True, blank=True, verbose_name='godzin pracowni')
    repetitions = models.IntegerField(null=True, blank=True, verbose_name='godzin repetytorium')
    seminars = models.IntegerField(null=True, blank=True, verbose_name='godzin seminariów')
    exercises_laboratiories = models.IntegerField(
        null=True, blank=True, verbose_name='godzin ćwiczenio-pracowni')

    deleted = models.BooleanField(verbose_name='ukryty', default=False)
    owner = models.ForeignKey(
        'users.Employee',
        verbose_name='opiekun',
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name='odnośnik (nazwa pojawiająca się w urlach)',
        null=True)

    created = models.DateTimeField(verbose_name='Utworzono', auto_now_add=True)
    edited = models.DateTimeField(verbose_name='Ostatnia zmiana', auto_now=True)

    in_prefs = models.BooleanField(verbose_name='w preferencjach', default=False)

    dyskretna_l = models.BooleanField(default=False,
                                      verbose_name='Przedmiot posiada również wersje: Dyskretna (L)')
    numeryczna_l = models.BooleanField(
        default=False,
        verbose_name='Przedmiot posiada również wersje: Numeryczna (L)')
    algorytmy_l = models.BooleanField(default=False,
                                      verbose_name='Przedmiot posiada również wersje: Algorytmy (L)')
    programowanie_l = models.BooleanField(
        default=False, verbose_name='Przedmiot posiada również wersje: Programowanie (L)')

    usos_kod = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default='',
        verbose_name='Kod przedmiotu w usos',
        help_text='UWAGA! Nie edytuj tego pola sam!')

    ue = models.BooleanField(
        default=False,
        verbose_name='Przedmiot prowadzony przy pomocy środków pochodzących z Unii Europejskiej')

    tags = models.ManyToManyField(Tag, through='TagCourseEntity')
    effects = models.ManyToManyField(Effects, verbose_name='Grupa efektów kształcenia', blank=True)

    objects = WithInformation()
    simple = models.Manager()
    noremoved = NoRemoved()
    statistics = StatisticsManager()

    def _add_or_none(self, hours1, hours2):
        """
        Adds two numbers denoting the number
        of hours of a particular type of class.
        If both are None, returns None, otherwise it
        returns the sum, possibly casting None to 0
        """
        if hours1 is None and hours2 is None:
            return None

        return (hours1 or 0) + (hours2 or 0)

    def get_lectures(self):
        return self._add_or_none(self.lectures, self.information.lectures)

    def get_exercises(self):
        return self._add_or_none(self.exercises, self.information.exercises)

    def get_laboratories(self):
        return self._add_or_none(self.laboratories, self.information.laboratories)

    def get_repetitions(self):
        return self._add_or_none(self.repetitions, self.information.repetitions)

    def get_seminars(self):
        return self._add_or_none(self.seminars, self.information.seminars)

    def get_exercises_laboratiories(self):
        return self._add_or_none(
            self.exercises_laboratiories,
            self.information.exercises_laboratories)

    def get_status(self):
        return self.status

    def effects_count(self):
        return self.effects.count()

    def mark_as_accepted(self):
        self.status = CourseEntity.STATUS_IN_OFFER

    def mark_for_review(self):
        self.status = CourseEntity.STATUS_FOR_REVIEW

    def mark_for_voting(self):
        self.status = CourseEntity.STATUS_TO_VOTE

    def is_proposal(self):
        return (self.status == CourseEntity.STATUS_PROPOSITION) \
            or (self.status == CourseEntity.STATUS_FOR_REVIEW)

    def save(self, *args, **kwargs):
        """
        Overloaded save method - during save autocreate slug field

        @param args: like model save args
        @param kwargs: like model save kwargs
        @return: nothing
        """
        super(CourseEntity, self).save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify('%d_%s' % (self.pk, self.name,))
            self.save()

    def __str__(self):
        return '%s' % (self.name, )

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'courses'
        # FIXME: this should not be needed, the modeltranslation lib
        # should automatically fall back to the Polish base name
        # (it's the default + we have it defined in settings.py)
        # For whatever reason Course instances (that use entity__name) are
        # actually ordered properly, but when accessing CourseEntity directly
        # it doesn't work...
        # As it is, we need this so lists in the offer app are sorted properly
        ordering = ['name_pl']

    def get_points(self, student: Optional[Student] = None) -> int:
        """Returns credits value of the course for the given student.

        If student is not provided, the function will return the default value.
        """
        from apps.enrollment.courses.models.points import StudentPointsView
        return StudentPointsView.course_value_for_student(student, self.pk)

    def get_short_name(self):
        """
        Return short name if present (e.g. JFiZO = Języki Formalne
        i Złożoność Obliczeniowa). Otherwise return full name.

        @return: String
        """
        if self.shortName is None:
            return self.name
        else:
            return self.shortName

    @cache_result
    def get_all_effects(self):
        return list(self.effects.all())

    @cache_result
    def get_all_tags(self):
        return list(self.tags.all())

    @cache_result
    def get_all_tags_with_weights(self):
        """
        TagCourseEntity is a glue model that contains extra info
        about the relationship - in this case, the "weight" of the tag.
        """
        return list(TagCourseEntity.objects.filter(courseentity=self))

    @cache_result_for(60 * 60)
    def serialize_for_json(self):
        """
        Serialize this object to a dictionary
        that contains the most important information and can
        be passed to a template or json.dumps
        """
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.get_short_name(),
            "status": self.status,
            "slug": self.slug,
            "type": self.type.id if self.type else -1,
            "english": self.english,
            "exam": self.exam,
            "semester": self.semester,
            "suggested_for_first_year": self.suggested_for_first_year,
            "teacher": self.owner.id if self.owner else -1,
            "effects": [effect.pk for effect in self.get_all_effects()],
            "tags": [tag.pk for tag in self.get_all_tags()]
        }

    @property
    def description(self):
        if self.information:
            return self.information.description
        else:
            return None

    @property
    def have_review_lecture(self):
        """
        Return True if entity have more than 0 hours of repetitions

        @return: Boolean
        """
        return self.repetitions and self.repetitions > 0

    @property
    def have_lecture(self):
        """
        Return True if entity have more than 0 hours of lecture

        @return: Boolean
        """
        return self.lectures and self.lectures > 0

    @property
    def have_tutorial(self):
        """
        Return True if entity have more than 0 hours of tutorial

        @return: Boolean
        """
        return self.exercises and self.exercises > 0

    @property
    def have_lab(self):
        """
        Return True if entity have more than 0 hours of laboratiories

        @return: Boolean
        """
        return self.laboratories and self.laboratories > 0

    @property
    def have_tutorial_lab(self):
        """
        Return True if entity have more than 0 hours of mixed tutorial and labs

        @return: Boolean
        """
        return self.exercises_laboratiories and self.exercises_laboratiories > 0

    @property
    def have_seminar(self):
        """
        Return True if entity have more than 0 hours of seminars

        @return: Boolean
        """
        return self.seminars and self.seminars > 0

    def is_summer(self):
        """
        Return True if entity is in summer semester

        @return Boolean
        """
        return self.semester == 'l'

    def is_winter(self):
        """
        Return True if entity is in winter semester

        @return Boolean
        """
        return self.semester == 'z'

    def is_in_voting(self):
        return self.status == CourseEntity.STATUS_TO_VOTE

    def get_all_voters(self, year=None):
        from apps.offer.vote.models.single_vote import SingleVote
        from apps.offer.vote.models.system_state import SystemState

        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)

        votes = SingleVote.objects.filter(
            value__gte=1, state=current_state, entity=self).select_related(
            'student', 'student__user').order_by('student__matricula')

        return [vote.student for vote in votes]

    @staticmethod
    def get_vote():
        return CourseEntity.noremoved.filter(status=CourseEntity.STATUS_TO_VOTE)

    @staticmethod
    def get_proposals(is_authenticated=False):
        # TODO: in the order_by clause, we could just use "name";
        # the model translation plugin will actually check the user's language
        # (based on the account settings if logged in, or headers otherwise)
        # and map it to name_en or name_pl accordingly. The trouble is, almost all
        # CourseEntities have empty English names, so the sorting order is nonsensical.
        # Could re-enable this when (if) we have proper translations for course names.
        result = CourseEntity.noremoved \
            .exclude(status=CourseEntity.STATUS_PROPOSITION) \
            .exclude(status=CourseEntity.STATUS_FOR_REVIEW) \
            .select_related('type', 'owner', 'owner__user') \
            .order_by('name_pl')

        if is_authenticated:
            return result

        else:
            return result.exclude(status=CourseEntity.STATUS_WITHDRAWN)

    @staticmethod
    def get_proposal(slug):
        proposal = CourseEntity.noremoved.get(slug=slug)
        try:
            information = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except IndexError:
            information = None

        proposal.information = information
        return proposal


class Related(models.Manager):
    """ Manager for course objects with visible semester """

    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(Related, self).get_queryset().select_related('semester', 'entity')


class VisibleManager(Related):
    """ Manager for course objects with visible semester """

    def get_queryset(self):
        """ Returns all courses which have marked semester as visible """
        return super(VisibleManager, self).get_queryset().filter(semester__visible=True)


class Course(models.Model):
    """
    Instacja Przedmiotu w danym semestrze
    """
    entity = models.ForeignKey(
        CourseEntity,
        verbose_name='podstawa przedmiotu',
        on_delete=models.CASCADE)
    information = models.ForeignKey(
        'CourseDescription',
        verbose_name='opis',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    semester = models.ForeignKey(
        'Semester',
        null=True,
        verbose_name='semestr',
        on_delete=models.CASCADE)

    notes = models.TextField(null=True, blank=True, verbose_name='uwagi do tej edyci przedmiotu')
    web_page = models.URLField(verbose_name='Strona WWW przedmiotu',
                               blank=True,
                               null=True)

    english = models.BooleanField(default=False, verbose_name='przedmiot prowadzony w j.angielskim')
    # chceck this!
    students_options = models.ManyToManyField('users.Student',
                                              verbose_name='opcje studentów',
                                              through='StudentOptions')

    records_start = models.DateTimeField(verbose_name='Początek zapisów', null=True, blank=True)
    records_end = models.DateTimeField(verbose_name='Koniec zapisów', null=True, blank=True)

    objects = DefaultCourseManager()
    simple = models.Manager()
    visible = VisibleManager()

    """
    getters
    """
    @property
    def owner(self):
        return self.entity.owner

    @property
    def exam(self):
        return self.entity.exam

    @property
    def suggested_for_first_year(self):
        return self.entity.suggested_for_first_year

    @property
    def name(self):
        return self.entity.name

    @property
    def description(self):
        return self.information.description

    @property
    def type(self):
        return self.entity.type

    @property
    def lectures(self):
        if self.entity.lectures:
            hours = self.entity.lectures
        else:
            hours = 0
        if self.information.lectures:
            delta = self.information.lectures
        else:
            delta = 0

        return hours + delta

    @property
    def repetitions(self):
        if self.entity.repetitions:
            hours = self.entity.repetitions
        else:
            hours = 0

        if self.information.repetitions:
            delta = self.information.repetitions
        else:
            delta = 0

        return hours + delta

    @property
    def exercises(self):
        if self.entity.exercises:
            hours = self.entity.exercises
        else:
            hours = 0
        if self.information.exercises:
            delta = self.information.exercises
        else:
            delta = 0

        return hours + delta

    @property
    def exercises_laboratories(self):
        if self.entity.exercises_laboratiories:
            hours = self.entity.exercises_laboratiories
        else:
            hours = 0
        if self.information.exercises_laboratories:
            delta = self.information.exercises_laboratories
        else:
            delta = 0

        return hours + delta

    @property
    def laboratories(self):
        if self.entity.laboratories:
            hours = self.entity.laboratories
        else:
            hours = 0
        if self.information.laboratories:
            delta = self.information.laboratories
        else:
            delta = 0

        return hours + delta

    @property
    def seminars(self):
        if self.entity.seminars:
            hours = self.entity.seminars
        else:
            hours = 0
        if self.information.seminars:
            delta = self.information.seminars
        else:
            delta = 0

        return hours + delta

    @property
    def requirements(self):
        return self.information.requirements

    def save(self, *args, **kwargs):
        super(Course, self).save(*args, **kwargs)

        if not self.slug:
            self.slug = slugify('%d %s' % (self.pk, self.entity.name))
            self.save()

    def get_absolute_url(self):
        return reverse('course-page', args=[str(self.slug)])

    def get_all_enrolled_emails(self):
        from apps.enrollment.records.models import Record, RecordStatus
        return Record.objects.filter(
            group__course=self, status=RecordStatus.ENROLLED
        ).values_list(
            'student__user__email', flat=True
        ).distinct()

    def votes_count(self, semester=None):
        from apps.offer.vote.models import SingleVote
        return SingleVote.objects.filter(
            Q(course=self),
            Q(state__semester_summer=self.semester) | Q(state__semester_winter=self.semester)
        ).count()

    def get_semester_name(self):
        """ returns name of semester course is linked to """
        if self.semester is None:
            logger.warning('Course.get_semester_name() was invoked with non unknown semester.')
            return "nieznany semestr"
        else:
            return self.semester.get_name()

    def get_points(self, student: Optional[Student] = None) -> int:
        """Returns credits value of the course for the given student.

        If student is not provided, the function will return the default value.
        """
        return self.entity.get_points(student)

    def get_effects_list(self):
        return self.entity.get_all_effects()

    def get_tags_list(self):
        return self.entity.get_all_tags()

    def get_was_enrolled(self, student):
        if student is None:
            return False

        # TODO
        return False

    @cache_result
    def get_type_id(self):
        return self.type.id if self.type.id else 1

    def serialize_for_json(self, student=None,
                           terms=None, includeWasEnrolled=False):
        from django.urls import reverse

        data = self.entity.serialize_for_json()
        data['id'] = self.pk
        data['type'] = self.get_type_id()
        data['url'] = reverse('course-page', args=[self.slug])
        if student is not None:
            is_recording_open = self.is_recording_open_for_student(student)
        else:
            is_recording_open = False
        data['is_recording_open'] = is_recording_open

        # TODO: why do we have this field defined in the model
        # if the CourseEntity object has it as well? What's the difference?
        data['english'] = self.english

        if includeWasEnrolled:
            data.update({
                'was_enrolled': self.get_was_enrolled(student)
            })

        if terms is not None:
            data.update({
                'terms': [term.serialize_for_json() for term in terms]
            })

        return data

    def has_exam_reservation(self):
        """
            Return True if  Course have reservation for exam
        """

        from apps.schedule.models.event import Event

        if not self.exam:
            return False

        if Event.objects.filter(course=self, type='0').exists():
            return True

        return False

    @staticmethod
    def get_courses_with_exam(semester):
        return Course.objects.filter(semester=semester, entity__exam=True)

    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'courses'
        ordering = ['entity__name']
        permissions = (
            ("view_stats", "Może widzieć statystyki"),
        )

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())


def recache(sender, **kwargs):
    mcache.clear()

#
# signals.post_save.connect(recache)
# signals.post_delete.connect(recache)


class CourseDescription(models.Model):
    """
    Przechowuje rewizję informacji o przedmiocie.
    Powiązania: :model:'course.CourseEntity'
    """

    # Podstawa do ktorej jestesmy przypisani
    entity = models.ForeignKey(CourseEntity, on_delete=models.CASCADE)
    author = models.ForeignKey('users.Employee', on_delete=models.CASCADE)

    is_ready = models.BooleanField(default=False)

    description = models.TextField(verbose_name='opis', blank=True, default='')

    lectures = models.IntegerField(
        verbose_name='różnica w godzinach wykładu',
        blank=True,
        null=True,
        default=0)
    repetitions = models.IntegerField(
        verbose_name='różnica w godzinach repetytoriów',
        blank=True,
        null=True,
        default=0)
    exercises = models.IntegerField(
        verbose_name='różnica w godzinach ćwiczeń',
        blank=True,
        null=True,
        default=0)
    laboratories = models.IntegerField(
        verbose_name='różnica w godzinach pracowni',
        blank=True,
        null=True,
        default=0)
    seminars = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name='różnica w godzinach seminariów')
    exercises_laboratories = models.IntegerField(
        verbose_name='różnica w godzinach ćw+prac', blank=True, null=True, default=0)

    requirements = models.ManyToManyField(
        CourseEntity,
        verbose_name='wymagania',
        related_name='+',
        blank=True)
    exam = models.BooleanField(verbose_name='egzamin', default=False)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'courses'

    def __str__(self):
        title = str(self.created) + " - "
        if self and self.author:
            title = title + str(self.author)
        return title

    def save_as_copy(self):
        self.id = None
        self.save(force_insert=True)


"""
Because a tag will have different weights for each
CourseEntity it's assigned to, we need this special
relationship glue model.
"""


class TagCourseEntity(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    courseentity = models.ForeignKey(CourseEntity, on_delete=models.CASCADE)
    weight = models.IntegerField(verbose_name='Waga')

    class Meta:
        app_label = 'courses'

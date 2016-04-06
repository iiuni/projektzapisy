# -*- coding: utf-8 -*-

from datetime import date
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.core.cache import cache as mcache
from apps.enrollment.courses.models.effects import Effects
from apps.enrollment.courses.models.tag import Tag

from apps.offer.proposal.exceptions import NotOwnerException

import logging

logger = logging.getLogger()


class WithInformation(models.Manager):
    """ Manager for course objects with visible semester """

    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(WithInformation, self).get_query_set().select_related('information')


class NoRemoved(WithInformation):
    """ Manager for course objects with visible semester """

    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(NoRemoved, self).get_query_set().filter(deleted=False, owner__isnull=False)


class SimpleManager(models.Manager):
    def get_with_opening(self, student):
        return self.ex


class DefaultCourseManager(models.Manager):
    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(DefaultCourseManager, self).get_query_set().select_related('entity', 'information')


class StatisticsManager(models.Manager):
    def in_year(self, year=None):
        from apps.offer.vote.models import SystemState

        if not year:
            year = date.today().year

        state = SystemState.get_state(year)

        #TODO: po przeniesieniu wszystkich metod do managerów filtrowanie na
        #  status powinno byc  z dziedziczenia
        return self.get_query_set().filter(status=3)\
            .select_related('type', 'owner', 'owner__user')\
            .order_by('name')\
            .extra(
                select={
                    'votes': "COALESCE((SELECT SUM(vote_singlevote.correction) FROM vote_singlevote WHERE"
                             " vote_singlevote.entity_id = courses_courseentity.id"
                             " AND vote_singlevote.state_id = %d), 0)" % state.id,
                    'voters': "SELECT COUNT(*) FROM vote_singlevote WHERE"
                              " vote_singlevote.entity_id = courses_courseentity.id "
                              "AND vote_singlevote.correction > 0 "
                              "AND vote_singlevote.state_id = %d" % state.id,
                    'maxpoints_votes': "COALESCE((SELECT SUM(vote_singlevote.correction) FROM vote_singlevote WHERE"
                              " vote_singlevote.correction = 3 "
                             " AND vote_singlevote.entity_id = courses_courseentity.id"
                             " AND vote_singlevote.state_id = %d), 0)" % state.id,
                    'maxpoints_voters': "SELECT COUNT(*) FROM vote_singlevote WHERE"
                              " vote_singlevote.entity_id = courses_courseentity.id "
                              "AND vote_singlevote.correction = 3 "
                              "AND vote_singlevote.state_id = %d" % state.id
                }
            )


statuses = ((0, u'Propozycja'), (1, u'W ofercie'), (2, u'Poddana pod głosowanie'),
            (3, u'Poddana pod głosowanie 2013'), (4, u'Wycofany z oferty'), (5, 'Do poprawienia'), )
semesters = (('u', 'nieoznaczony'), ('z', 'zimowy'), ('l', 'letni'))
ectslist = [(x, str(x)) for x in range(1, 16)]


class CourseEntity(models.Model):
    """entity of particular course title"""

    information = models.ForeignKey('CourseDescription', null=True, blank=True)

    #Test name
    name = models.CharField(max_length=100,
                            verbose_name='nazwa')
    shortName = models.CharField(max_length=30,
                                 verbose_name='skrócona nazwa',
                                 null=True, blank=True,
                                 help_text=u'Opcjonalna skrócona nazwa, używana na np. planie. Przykłady: JFiZO, AiSD')

    status = models.IntegerField(choices=statuses, default=0)

    semester = models.CharField(max_length=1, choices=semesters, default='u', verbose_name='semestr')

    type = models.ForeignKey('Type',
                             verbose_name='rodzaj',
                             null=True)
    english = models.BooleanField(default=False,
                                  verbose_name='przedmiot prowadzony w j.angielskim')
    exam = models.BooleanField(verbose_name='egzamin',
                               default=True)

    suggested_for_first_year = models.BooleanField(verbose_name='polecany dla pierwszego roku')

    web_page = models.URLField(verbose_name='strona www', null=True, blank=True)
    ects = models.IntegerField(null=True, blank=True)
    lectures = models.IntegerField(null=True, blank=True, verbose_name=u'godzin wykładu')
    exercises = models.IntegerField(null=True, blank=True, verbose_name=u'godzin ćwiczeń')
    laboratories = models.IntegerField(null=True, blank=True, verbose_name=u'godzin pracowni')
    repetitions = models.IntegerField(null=True, blank=True, verbose_name=u'godzin repetytorium')
    seminars = models.IntegerField(null=True, blank=True, verbose_name=u'godzin seminariów')
    exercises_laboratiories = models.IntegerField(null=True, blank=True, verbose_name=u'godzin ćwiczenio-pracowni')

    deleted = models.BooleanField(verbose_name='ukryty', default=False)
    owner = models.ForeignKey('users.Employee', verbose_name='opiekun', blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik (nazwa pojawiająca się w urlach)',
                            null=True)

    created = models.DateTimeField(verbose_name='Utworzono', auto_now_add=True)
    edited = models.DateTimeField(verbose_name='Ostatnia zmiana', auto_now=True)

    in_prefs = models.BooleanField(verbose_name='w preferencjach', default=True)

    dyskretna_l = models.BooleanField(default=False, verbose_name=u'Przedmiot posiada również wersje: Dyskretna (L)')
    numeryczna_l = models.BooleanField(default=False, verbose_name=u'Przedmiot posiada również wersje: Numeryczna (L)')
    algorytmy_l = models.BooleanField(default=False, verbose_name=u'Przedmiot posiada również wersje: Algorytmy (L)')
    programowanie_l = models.BooleanField(default=False,
                                          verbose_name=u'Przedmiot posiada również wersje: Programowanie (L)')

    usos_kod = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=u'Kod przedmiotu w usos',
                                help_text='UWAGA! Nie edytuj tego pola sam!')

    ue = models.BooleanField(default=False,
                             verbose_name=u'Przedmiot prowadzony przy pomocy środków pochodzących z Unii Europejskiej')

    tags = models.ManyToManyField(Tag, through='TagCourseEntity')
    effects = models.ManyToManyField(Effects, verbose_name=u'Grupa efektów kształcenia', null=True, blank=True)

    objects = WithInformation()
    simple = models.Manager()
    noremoved = NoRemoved()
    statistics = StatisticsManager()


    def get_lectures(self):
        return self.lectures + self.information.lectures

    def get_exercises(self):
        return self.lectures + self.information.lectures

    def get_laboratories(self):
        return self.laboratories + self.information.laboratories

    def get_repetitions(self):
        return self.repetitions + self.information.repetitions

    def get_seminars(self):
        return self.seminars + self.information.seminars

    def get_exercises_laboratiories(self):
        return self.exercises_laboratiories + self.information.exercises_laboratories

    #

    def get_status(self):
        return self.status

    def effects_count(self):
        return self.effects.count()

    def mark_as_accepted(self):
        self.status = 1

    def mark_for_review(self):
        self.status = 5

    def mark_for_voting(self):
        self.status = 3

    def is_proposal(self):
        return (self.status == 0) or (self.status == 5)

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

        super(CourseEntity, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % (self.name, )

    class Meta:
        verbose_name = 'Podstawa przedmiotu'
        verbose_name_plural = 'Podstawy przedmiotów'
        app_label = 'courses'
        ordering = ['name']


    def get_opening_time(self, student):
        """

        @param student:
        @return:
        """

        from apps.users.models import OpeningTimesView

        return OpeningTimesView.objects.get(student=student, course=self)


    def get_points(self, student=None):
        from apps.enrollment.courses.models import StudentPointsView, PointsOfCourseEntities

        if student:
            try:
                points = StudentPointsView.objects.get(student=student, entity=self)
                return points
            except ObjectDoesNotExist:
                pass
        try:
            return PointsOfCourseEntities.objects.filter(entity=self, program__isnull=True)[0]
        except (ObjectDoesNotExist, IndexError) as e:
            return None


    def get_short_name(self):
        """
        If entity have shortName (e.g. JFiZO for Języki Formalne i Złożoność Obliczeniowa) return it.
        Otherwise return full name

        @return: String
        """
        if self.shortName is None:
            return self.name
        else:
            return self.shortName


    @property
    def description(self):
        return self.information.description


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
        return self.status == 3

    def get_all_voters(self, year=None):
        from apps.offer.vote.models.single_vote import SingleVote
        from apps.offer.vote.models.system_state import SystemState

        if not year:
            year = date.today().year
        current_state = SystemState.get_state(year)

        votes = SingleVote.objects.filter(value__gte=1, state=current_state, entity=self).select_related('student',
                                                                                                         'student__user').order_by(
            'student__matricula')

        return [vote.student for vote in votes]

    @staticmethod
    def get_vote():
        return CourseEntity.noremoved.filter(status=3)

    @staticmethod
    def get_voters():
        from apps.offer.vote.models.single_vote import SingleVote
        from apps.offer.vote.models.system_state import SystemState

        year = date.today().year
        current_state = SystemState.get_state(year)

        return SingleVote.objects.distinct('student').filter(state=current_state)

    @staticmethod
    def get_proposals():
        return CourseEntity.noremoved.filter(status__gte=1) \
            .select_related('type', 'owner', 'owner__user')

    @staticmethod
    def get_proposal(slug):
        proposal = CourseEntity.noremoved.get(slug=slug)
        try:
            information = CourseDescription.objects.filter(entity=proposal).order_by('-id')[0]
        except IndexError:
            information = None

        proposal.information = information
        return proposal

    @staticmethod
    def get_employee_proposals(user):
        return CourseEntity.noremoved.filter(owner=user.employee)

    @staticmethod
    def get_employee_proposal(user, slug):
        proposal = CourseEntity.noremoved.get(slug=slug)

        if user.is_staff or proposal.owner == user.employee:
            return proposal
        else:
            raise NotOwnerException


class Related(models.Manager):
    """ Manager for course objects with visible semester """

    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(Related, self).get_query_set().select_related('semester', 'type', 'type__classroom', 'entity')


class VisibleManager(Related):
    """ Manager for course objects with visible semester """

    def get_query_set(self):
        """ Returns all courses which have marked semester as visible """
        return super(VisibleManager, self).get_query_set().filter(semester__visible=True)


class Course(models.Model):
    """
    Instacja Przedmiotu w danym semestrze
    """
    entity = models.ForeignKey(CourseEntity, verbose_name='podstawa przedmiotu')
    information = models.ForeignKey('CourseDescription', verbose_name='opis', null=True, blank=True)

    slug = models.SlugField(max_length=255, unique=True, verbose_name='odnośnik', null=True)
    semester = models.ForeignKey('Semester', null=True, verbose_name='semestr')
    teachers = models.ManyToManyField('users.Employee', verbose_name='prowadzący', blank=True)

    notes = models.TextField(null=True, blank=True, verbose_name='uwagi do tej edyci przedmiotu')
    web_page = models.URLField(verbose_name='Strona WWW przedmiotu',
                               verify_exists=True,
                               blank=True,
                               null=True)

    english = models.BooleanField(default=False, verbose_name='przedmiot prowadzony w j.angielskim')
    #chceck this!
    students_options = models.ManyToManyField('users.Student',
                                              verbose_name='opcje studentów',
                                              through='StudentOptions')

    records_start = models.DateTimeField(verbose_name=u'Początek zapisów', null=True, blank=True)
    records_end = models.DateTimeField(verbose_name=u'Koniec zapisów', null=True, blank=True)

    objects = DefaultCourseManager()
    simple = models.Manager()
    visible = VisibleManager()

    """
    getters
    """

    def enrollments_are_open(self):
        if self.records_end and self.records_start and self.records_start <= datetime.datetime.now() <= self.records_end:
            return True

        if datetime.datetime.now() <= self.semester.records_closing:
            return True

        return False


    def get_opening_time(self, student):
        """

        @param student:
        @return:
        """

        from apps.users.models import OpeningTimesView

        return OpeningTimesView.objects.get(student=student, course=self)

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
    def tags(self):
        if not hasattr(self, '_tagscache'):
            self._tagscache = TagCourseEntity.objects.filter(courseentity=self.entity)

        return self._tagscache


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
        if not self.slug:
            self.slug = slugify('%d %s %s' % (self.pk, self.entity.name))

        super(Course, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('course-page', args=[str(self.slug)])

    def student_is_in_ects_limit(self, student):
        #TODO: test me!
        from apps.enrollment.courses.models import Semester

        semester = Semester.get_current_semester()

        return semester.get_current_limit() < student.get_ects_with_course(semester, self)


    def get_all_enrolled_emails(self):
        from apps.enrollment.records.models import Record

        return Record.objects.filter(group__course=self, status='1').values_list('student__user__email',
                                                                                 flat=True).distinct()


    def votes_count(self, semester=None):
        from apps.offer.vote.models import SingleVote

        return SingleVote.objects \
            .filter(Q(course=self), Q(state__semester_summer=self.semester) | Q(state__semester_winter=self.semester)) \
            .count()

    def is_opened(self, student):
        try:
            return self.get_opening_time(student).opening_time < datetime.datetime.now()
        except:
            return False

    def is_recording_open_for_student(self, student=None):
        """ gives the answer to question: is course opened for apps.enrollment for student at the very moment? """

        if not student:
            return False

        records_opening = self.semester.records_opening
        records_closing = self.semester.records_closing

        now = datetime.datetime.now()

        if self.records_start and self.records_end and self.records_start <= now <= self.records_end:
            return True

        if records_opening and self.is_opened(student) and now < records_closing:
            return True

        if self.records_start and self.records_end and self.records_start <= now < self.records_end:
            return True

        return False

    def get_enrollment_opening_time(self, student):
        """ returns course opening time as datetime object or None if course is opened / was opened """
        records_opening = self.semester.records_opening
        from apps.offer.vote.models.single_vote import SingleVote

        try:
            vote = SingleVote.objects.get(Q(course=self), Q(student=student),
                                          Q(state__semester_winter=self.semester) | Q(
                                              state__semester_summer=self.semester))
            interval = datetime.timedelta(minutes=(-1440) * vote.correction + 4320)
        except ObjectDoesNotExist:
            interval = datetime.timedelta(minutes=4320)

        if records_opening == None:
            return False
        else:
            student_opening = records_opening - student.get_t0_interval()
            if student_opening + interval < datetime.datetime.now():
                return None
            else:
                return student_opening + interval

    def get_semester_name(self):
        """ returns name of semester course is linked to """
        if self.semester is None:
            logger.warning('Course.get_semester_name() was invoked with non unknown semester.')
            return "nieznany semestr"
        else:
            return self.semester.get_name()

    def get_points(self, student=None):
        """
            @param student: (optional) :model:'users.Student'

            @return :model:'courses.Points' or :model:'courses.PointsOfCourseEntities' both have the same interface
        """

        return self.entity.get_points(student)


    def serialize_for_ajax(self, student=None, is_recording_open=None):
        from django.core.urlresolvers import reverse

        data = {
            'id': self.pk,
            'name': self.name,
            'short_name': self.entity.get_short_name(),
            'type': self.type.id and self.type.id or 1,
            'url': reverse('course-page', args=[self.slug]),
            'is_recording_open': is_recording_open is not None and is_recording_open or (False if (student is None) else \
                                                                                             self.is_recording_open_for_student(
                                                                                                 student))
        }

        return data


    def has_exam_reservation(self):
        """
            Return True if  Course have reservation for exam
        """

        from apps.schedule.models import Event

        if not self.exam:
            return False

        if Event.objects.filter(course=self, type='0').exists():
            return True

        return False

    @staticmethod
    def get_courses_with_exam(semester):
        return Course.objects.filter(semester=semester, entity__exam=True)

    @staticmethod
    def get_student_courses_in_semester(student, semester):
        from apps.enrollment.records.models import Record

        return Record.objects.select_related('group', 'group__teacher', 'group__course',
                                             'group__course__entity').prefetch_related('group__term',
                                                                                       'group__term__classrooms').filter(
            status='1', student=student, group__course__semester=semester). \
            extra(select={'points': 'SELECT value FROM courses_studentpointsview WHERE student_id='
                                    + str(student.id) + ' AND entity_id=courses_course.entity_id'}).order_by(
            'group__course__entity__name')

    class Meta:
        verbose_name = 'przedmiot'
        verbose_name_plural = 'przedmioty'
        app_label = 'courses'
        ordering = ['entity__name']
        permissions = (
            ("view_stats", u"Może widzieć statystyki"),
        )

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.get_semester_name())


def recache(sender, **kwargs):
    mcache.clear()

#
#signals.post_save.connect(recache)
#signals.post_delete.connect(recache)


class CourseDescription(models.Model):
    """
    Przechowuje rewizję informacji o przedmiocie.
    Powiązania: :model:'course.CourseEntity'
    """

    entity = models.ForeignKey(CourseEntity) #Podstawa do ktorej jestesmy przypisani
    author = models.ForeignKey('users.Employee')

    is_ready = models.BooleanField()

    description = models.TextField(verbose_name='opis', blank=True, default='')

    lectures = models.IntegerField(verbose_name=u'różnica w godzinach wykładu', blank=True, null=True, default=0)
    repetitions = models.IntegerField(verbose_name=u'różnica w godzinach repetytoriów', blank=True, null=True,
                                      default=0)
    exercises = models.IntegerField(verbose_name=u'różnica w godzinach ćwiczeń', blank=True, null=True, default=0)
    laboratories = models.IntegerField(verbose_name=u'różnica w godzinach pracowni', blank=True, null=True, default=0)
    seminars = models.IntegerField(default=0, null=True, blank=True, verbose_name=u'różnica w godzinach seminariów')
    exercises_laboratories = models.IntegerField(verbose_name=u'różnica w godzinach ćw+prac', blank=True, null=True,
                                                 default=0)

    requirements = models.ManyToManyField(CourseEntity, verbose_name='wymagania', related_name='+', blank=True)
    exam = models.BooleanField(verbose_name='egzamin')

    created = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'courses'

    def __unicode__(self):
        title = smart_unicode(self.created) + " - "
        if self and self.author:
            title = title + smart_unicode(self.author)
        return title

    def save_as_copy(self):
        self.id = None
        self.save(force_insert=True)        

class TagCourseEntity(models.Model):
    tag = models.ForeignKey(Tag)
    courseentity = models.ForeignKey(CourseEntity)
    weight = models.IntegerField(verbose_name=u'Waga')

    class Meta:
        app_label = 'courses'

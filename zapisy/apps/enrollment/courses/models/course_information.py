"""Defines Courses models.

The entire course information is modeled by the CourseInformation class fields.
CourseInformation is a base class instantiated in Proposal (an abstract
Course entity spanning the years) and CourseInstance (Course being given in a
single semester).
"""
from typing import Dict

import choicesenum
from django.db import models
from django.template.defaultfilters import slugify

from apps.users.models import Employee

from .course_type import Type as CourseType
from .effects import Effects
from .tag import Tag


class Language(choicesenum.ChoicesEnum):
    ENGLISH = 'en', "angielski"
    POLISH = 'pl', "polski"


class CourseInformation(models.Model):
    """CourseInformation is a class defining a Course entirely.

    It is intended to be subclassed by Proposal (in the `offer/proposal` app)
    and Course (in this app).
    """

    name = models.CharField("nazwa przedmiotu", max_length=100)
    name_en = models.CharField("nazwa po angielsku", max_length=100, blank=True)
    short_name = models.CharField("skrócona nazwa przedmiotu", max_length=30, blank=True)
    slug = models.SlugField("identyfikator URL", unique=True, max_length=255)
    description = models.TextField("opis przedmiotu", blank=True)
    language = models.CharField(
        "język wykładowy", choices=Language.choices(), max_length=2, default=Language.POLISH)
    course_type = models.ForeignKey(CourseType, verbose_name="rodzaj", on_delete=models.PROTECT)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT)
    recommended_for_first_year = models.BooleanField(
        "przedmiot polecany dla pierwszego roku", default=False)
    points = models.PositiveSmallIntegerField("ECTS", default=6)

    has_exam = models.BooleanField("przedmiot z egzaminem", default=True)

    hours_lecture = models.PositiveSmallIntegerField("godzin wykładu", default=0)
    hours_exercise = models.PositiveSmallIntegerField("godzin ćwiczeń", default=0)
    hours_lab = models.PositiveSmallIntegerField("godzin pracowni", default=0)
    hours_exercise_lab = models.PositiveSmallIntegerField("godzin ćwiczenio-pracowni", default=0)
    hours_seminar = models.PositiveSmallIntegerField("godzin seminarium", default=0)
    hours_recap = models.PositiveSmallIntegerField("godzin repetytorium", default=0)

    # Fields for syllabus
    teaching_methods = models.TextField("metody kształcenia", blank=True)
    preconditions = models.TextField("wymagania wstępne", blank=True)
    objectives = models.TextField("cele przedmiotu", blank=True)
    contents = models.TextField("treści programowe", blank=True)
    teaching_effects = models.TextField("zakładane efekty kształcenia", blank=True)
    literature = models.TextField("literatura obowiązkowa i zalecana", blank=True)
    verification_methods = models.TextField(
        "metody weryfikacji zakładanych efektów kształcenia", blank=True)
    passing_means = models.TextField("Warunki i forma zaliczenia", blank=True)
    student_labour = models.TextField("nakład pracy studenta", blank=True)

    # These fields should remain hidden from all users and are only to fill by
    # the head of teaching. Their are required for the syllabus.
    teaching_unit = models.CharField("jednostka prowadząca przedmiot", max_length=100, blank=True)
    usos_kod = models.CharField("kod przedmiotu w USOS", max_length=20, blank=True, editable=False)
    major = models.CharField("kierunek studiów", max_length=100, blank=True)
    level = models.CharField("poziom studiów", max_length=100, blank=True)
    year = models.CharField("rok studiów", max_length=50, blank=True)
    discipline = models.CharField("dyscyplina", max_length=100, default="Informatyka")

    tags = models.ManyToManyField(Tag, verbose_name="tagi", blank=True)
    effects = models.ManyToManyField(Effects, verbose_name="grupy efektów kształcenia", blank=True)

    created = models.DateTimeField("Data utworzenia", auto_now_add=True)
    modified = models.DateTimeField("Data modyfikacji", auto_now=True)

    def save(self, *args, **kwargs):
        """Overrides standard Django `save` function."""
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f'{self.pk} {self.name}')
            self.save()

    def __str__(self):
        return self.name

    def __copy__(self) -> 'CourseInformation':
        """Returns a (shallow) copy of the CourseInformation object.

        All fields will be copied with exception of 'slug', 'usos_kod'. Names
        will be prepended with an indicator that the object is a clone.

        The returned object is not saved in the database.

        To use it run copy.copy on a model instance.
        """
        copy = CourseInformation.__new__(CourseInformation)

        # Copies all shallow fields from self to copy.
        copy.__dict__.update(self.__dict__)

        # This causes that when copy is saved, it becomes a new record.
        copy.pk = None

        # Clear some fields.
        copy.slug = None
        copy.usos_kod = None

        return copy

    def __json__(self):
        """Returns a JSON-serializable dict with al course information."""
        return {
            'id': self.id,
            'name': self.name,
            'courseType': self.course_type_id,
            'recommendedForFirstYear': self.recommended_for_first_year,
            'owner': self.owner_id,
            'effects': [effect.pk for effect in self.effects.all()],
            'tags': [tag.pk for tag in self.tags.all()],
        }

    def get_short_name(self):
        return self.short_name or self.name

    @staticmethod
    def prepare_filter_data(qs: models.QuerySet) -> Dict:
        """Prepares the data for course filter based on a given queryset."""
        all_effects = Effects.objects.all().values_list('id', 'group_name', named=True)
        all_tags = Tag.objects.all().values_list('id', 'full_name', named=True)
        all_owners = qs.values_list(
            'owner', 'owner__user__first_name', 'owner__user__last_name', named=True).distinct()
        all_types = qs.values_list('course_type', 'course_type__name', named=True).distinct()
        return {
            'allEffects': {e.id: e.group_name for e in all_effects},
            'allTags': {t.id: t.full_name for t in all_tags},
            'allOwners': {
                o.owner: [o.owner__user__first_name, o.owner__user__last_name] for o in all_owners
            },
            'allTypes': {c.course_type: c.course_type__name for c in all_types},
        }

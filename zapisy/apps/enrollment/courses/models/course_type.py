from django.db import models
import json


class Type(models.Model):
    """types of courses"""
    name = models.CharField(max_length=30, verbose_name='rodzaj zajec', default="", unique=False)
    short_name = models.CharField(
        max_length=5,
        verbose_name='rodzaj zajec (króŧka forma)',
        default="",
        unique=False)
    group = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name='grupa',
        on_delete=models.CASCADE)
    obligatory = models.BooleanField(default=False, verbose_name='przedmioty obowiązkowe')
    meta_type = models.BooleanField(default=False, verbose_name='Grupa typow')
    free_in_vote = models.BooleanField(default=False)

    have_review_lecture = models.BooleanField(verbose_name='Posiada repetytorium', default=False)
    have_lecture = models.BooleanField(verbose_name='Posiada wykład', default=False)
    have_tutorial = models.BooleanField(verbose_name='Posiada ćwiczenia', default=False)
    have_lab = models.BooleanField(verbose_name='Posiada pracownię', default=False)
    have_tutorial_lab = models.BooleanField(
        verbose_name='Posiada ćwiczenio-pracownię', default=False)
    have_seminar = models.BooleanField(verbose_name='Posiada seminarium', default=False)
    have_project = models.BooleanField(verbose_name='Posiada projekt', default=False)

    default_ects = models.IntegerField(verbose_name='Punkty ECTS', default=6)

    # TODO: dodać unique na parę (meta_type, name)

    class Meta:
        verbose_name = 'rodzaj przedmiotu'
        verbose_name_plural = 'rodzaje przedmiotów'
        app_label = 'courses'

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_for_jsfilter():
        return Type.objects.select_related('group').order_by('name').all()

    @staticmethod
    def get_types_for_syllabus():
        """
            Zwraca wszystkie typy wraz z informacją o typie zajęć (JSON).
        """
        types = Type.objects.all()
        types_dict = {}
        for t in types:
            types_dict[t.id] = {
                'lectures': t.have_lecture,
                'exercises': t.have_tutorial,
                'repetitions': t.have_review_lecture,
                'laboratories': t.have_lab,
                'exercises_laboratiories': t.have_tutorial_lab,
                'seminars': t.have_seminar,
                'default_ects': t.default_ects
            }
        return json.dumps(types_dict)

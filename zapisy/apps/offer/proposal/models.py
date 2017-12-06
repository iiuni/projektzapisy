# -*- coding: utf-8 -*-
from django.db import models
from apps.enrollment.courses.models import CourseEntity

class LearningMethod(models.Model):
    name = models.CharField(max_length=250, verbose_name='metoda kształcenia')
    
    class Meta:
        verbose_name = 'Metoda kształcenia'
        verbose_name_plural = 'Metody kształcenia'
        app_label = 'proposal'

    def __str__(self):
        return str(self.name)

studies_types = (('isim','isim'), ('inf','informatyka'), ('both','informatyka, ISIM'))
year_choices = [(x, str(x)) for x in range(1, 6)]

class Syllabus(models.Model):
    entity = models.OneToOneField(CourseEntity, verbose_name='podstawa przedmiotu', related_name='syllabus')

    studies_type = models.CharField(max_length=80, choices=studies_types, default='both', verbose_name='Kierunek studiów')
    year = models.IntegerField(null=True, blank=True, choices=year_choices, verbose_name='Rok studiów')
    requirements = models.TextField(verbose_name='Wymagania wstępne w zakresie wiedzy, umiejętności i kompetencji społecznych', blank=True, default='')
    objectives = models.TextField(verbose_name='Cele przedmiotu', blank=True, default='')
    effects_txt = models.TextField(verbose_name='Zakładane efekty kształcenia', blank=True, default='')
    effects_codes = models.TextField(verbose_name='Symbole kierunkowych efektów kształcenia', blank=True, default='', help_text='Wypełnia DDD')
    contents = models.TextField(verbose_name='Treści programowe', blank=True, default='')
    learning_methods = models.ManyToManyField(LearningMethod, verbose_name='Metody kształcenia', blank=True)
    literature = models.TextField(verbose_name='Zalecana literatura (podręczniki)', blank=True, default='')
    passing_form = models.TextField(verbose_name='Forma zaliczenia poszczególnych komponentów przedmiotu/modułu, sposób sprawdzenia osiągnięcia zamierzonych efektów kształcenia', blank=True, default='')
    exam_hours = models.IntegerField(null=True, blank=True, verbose_name="egzamin")
    tests_hours = models.IntegerField(null=True, blank=True, verbose_name="sprawdziany/kolokwia")
    project_presentation_hours = models.IntegerField(null=True, blank=True, verbose_name="prezentacja projektu")


    @property
    def name(self):
        return self.entity.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Metoda kształcenia'
        verbose_name_plural = 'Metody kształcenia'
        app_label = 'proposal'

    def __str__(self):
        return str(self.name)


class StudentWork(models.Model):
	name = models.CharField(max_length=250, verbose_name='nazwa aktywności')
	hours = models.IntegerField(verbose_name='liczba godzin')
	syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE)

	class Meta:
		verbose_name = 'Praca własna studenta'
		app_label = 'proposal'

	def __str__(self):
		return str(self.name)


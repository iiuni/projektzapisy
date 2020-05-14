from datetime import time
from django.urls import reverse

from django.db import models
from django.db.models import Q
from django_extensions.db.fields import AutoSlugField

floors = [(0, 'Parter'),
          (1, 'I piętro'),
          (2, 'II Piętro'),
          (3, 'III piętro')]

types = [(0, 'Sala wykładowa'),
         (1, 'Sala ćwiczeniowa'),
         (2, 'Pracownia komputerowa - Windows'),
         (3, 'Pracownia komputerowa - Linux'),
         (4, 'Pracownia dwusystemowa (Windows+Linux)'),
         (5, 'Poligon (109)')]


class Classroom(models.Model):
    """classroom in institute"""
    type = models.IntegerField(choices=types, default=1, verbose_name='typ')
    description = models.TextField(null=True, blank=True, verbose_name='opis')
    number = models.CharField(max_length=20, verbose_name='numer sali')
    # we don't use ordering properly
    order = models.IntegerField(null=True, blank=True)
    building = models.CharField(max_length=75, verbose_name='budynek', blank=True, default='')
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')
    floor = models.IntegerField(choices=floors, null=True, blank=True)
    can_reserve = models.BooleanField(default=False)
    slug = AutoSlugField(populate_from='number')

    usos_id = models.PositiveIntegerField(
        blank=True, null=True, unique=True, verbose_name='ID sali w systemie USOS')

    class Meta:
        verbose_name = 'sala'
        verbose_name_plural = 'sale'
        app_label = 'courses'
        ordering = ['floor', 'number']

    def get_absolute_url(self):
        try:
            return reverse('events:classroom', args=[self.slug])
        except BaseException:
            return reverse('events:classrooms')

    def __str__(self):
        return str(self.number) + ' (' + str(self.capacity) + ')'

    @classmethod
    def get_by_number(cls, number):
        return cls.objects.get(number=number)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def get_by_slug(cls, slug):
        return cls.objects.get(slug=slug)

    @classmethod
    def get_in_institute(cls, reservation=False):
        rooms = cls.objects.all()

        if reservation:
            rooms = rooms.filter(can_reserve=True).order_by('floor', 'number')

        return rooms

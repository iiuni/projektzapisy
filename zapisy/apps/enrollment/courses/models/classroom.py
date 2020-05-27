from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField


class Floors(models.IntegerChoices):
    GROUND_FLOOR = 0, 'Parter'
    FIRST_FLOOR = 1, 'I piętro'
    SEC_FLOOR = 2, 'II piętro'
    THIRD_FLOOR = 3, 'III piętro'


class Types(models.IntegerChoices):
    LECTURE_HALL = 0, 'Sala wykładowa'
    CLASSROOM = 1, 'Sala ćwiczeniowa'
    WINDOWS_LAB = 2, 'Pracownia komputerowa - Windows'
    LINUX_LAB = 3, 'Pracownia komputerowa - Linux'
    DOUBLE_OS_LAB = 4, 'Pracownia dwusystemowa (Windows+Linux)'
    POLIGON = 5, 'Poligon (109)'


class Classroom(models.Model):
    """Classroom in institute."""
    type = models.IntegerField(choices=Types.choices, default=Types.CLASSROOM, verbose_name='typ')
    description = models.TextField(null=True, blank=True, verbose_name='opis')
    number = models.CharField(max_length=20, verbose_name='numer sali')
    # we don't use ordering properly
    order = models.IntegerField(null=True, blank=True)
    building = models.CharField(max_length=75, verbose_name='budynek', blank=True, default='')
    capacity = models.PositiveSmallIntegerField(default=0, verbose_name='liczba miejsc')
    floor = models.IntegerField(choices=Floors.choices, null=True, blank=True)
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

from django.db import models
from django.shortcuts import reverse
from django.template.defaultfilters import slugify

from apps.offer.proposal.models import Proposal

from .course_information import CourseInformation
from .semester import Semester


class CourseInstance(CourseInformation):
    """Stores a course instance taught in a semester."""
    offer = models.ForeignKey(
        Proposal, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="oferta")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, verbose_name="semestr")

    # Course may have an individual enrollment period.
    records_start = models.DateTimeField("Początek zapisów", null=True, blank=True)
    records_end = models.DateTimeField("Koniec zapisów", null=True, blank=True)

    # A temporary field for migrations.
    old_course = models.OneToOneField(
        'courses.Course', null=True, blank=True, on_delete=models.SET_NULL, related_name='instance')

    class Meta:
        verbose_name = "Instancja przedmiotu"
        verbose_name_plural = "Instancje przedmiotów"

    def save(self, *args, **kwargs):
        """Overrides standard Django `save` function."""
        if not self.slug:
            self.slug = slugify(f'{self.name} {self.semester}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.semester})"

    def __json__(self):
        d = super().__json__()
        d.update({
            'url': reverse('course-page', args=[str(self.slug)]),
        })
        return d

from typing import Optional

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

    @classmethod
    def create_proposal_instance(cls, proposal: Proposal, semester: Semester):
        """Constructs an instance of the course in the semester."""
        proposal_dict = proposal.courseinformation_ptr.__dict__.copy()
        del proposal_dict['_state']
        del proposal_dict['id']
        del proposal_dict['slug']
        del proposal_dict['created']
        del proposal_dict['modified']
        proposal_dict.update({
            'semester': semester,
            'offer': proposal,
        })

        instance = cls(**proposal_dict)
        instance.save()
        instance.tags.set(proposal.tags.all())
        instance.effects.set(proposal.effects.all())
        return instance

    @classmethod
    def get_current_instance(cls, proposal: Proposal) -> Optional['CourseInstance']:
        """For a given proposal returns its currently taught instance or None.

        None is returned if the proposal is not currently taught.
        """
        semester = Semester.get_current_semester()
        if semester is None:
            return None
        try:
            return cls.objects.get(semester=semester, offer=proposal)
        except cls.DoesNotExist:
            return None

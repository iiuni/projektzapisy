"""This app helps the Head of Teaching assign employees to the course groups.

The Head of Teaching selects courses (proposals) and group types that are
understaffed. Then the employees can express their willingness to teach
different classes.
"""
from django.db import models

from apps.enrollment.courses.models.group import GROUP_TYPE_CHOICES
from apps.offer.proposal.models import Proposal
from apps.users.models import Employee


class PreferencesQuestionManager(models.Manager):
    """This manager automatically joins the queryset with proposal."""
    def get_queryset(self):
        return super().get_queryset().select_related('proposal')


class PreferencesQuestion(models.Model):
    """Contains all the classes, which employees need to set their preferences.

    A single question is a proposal-type pair defining a class that can be
    taught by an employee.
    """
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, verbose_name="przedmiot")
    class_type = models.CharField("typ zajęć", max_length=2, choices=GROUP_TYPE_CHOICES)

    objects = PreferencesQuestionManager()

    class Meta:
        verbose_name = "pytanie"
        verbose_name_plural = "pytania"
        unique_together = ('proposal', 'class_type')
        ordering = ['proposal']

    def __str__(self):
        return f"{self.proposal} | {self.get_class_type_display()}"


class PreferenceManager(models.Manager):
    """Automatically joins the queryset with employee, user and question."""
    def get_queryset(self):
        return super().get_queryset().select_related('employee', 'employee__user', 'question',
                                                     'question__proposal')


class Preference(models.Model):
    """A model representing employee's willingness to teach a class."""
    PREFERENCE_CHOICES = (
        (3, "Chętnie"),
        (2, "Być może"),
        (1, "Raczej nie"),
        (0, "Nie"),
    )

    employee = models.ForeignKey(Employee, verbose_name="pracownik", on_delete=models.CASCADE)
    question = models.ForeignKey(PreferencesQuestion,
                                 verbose_name="pytanie",
                                 on_delete=models.CASCADE)
    answer = models.PositiveSmallIntegerField("wola",
                                              choices=PREFERENCE_CHOICES,
                                              null=True,
                                              blank=True)

    objects = PreferenceManager()

    class Meta:
        verbose_name = "preferencja pracownika"
        verbose_name_plural = "preferencje pracowników"

        unique_together = ('employee', 'question')

    def __str__(self):
        return f"{self.employee.user.get_full_name()}, {self.question}: {self.get_answer_display()}"

    @staticmethod
    def make_preferences(employee: Employee):
        """Creates preferences for questions that do not have a preference
        object for the given employee.
        """
        existing_preferences = Preference.objects.filter(employee=employee).values_list(
            'question_id', flat=True)
        missing_questions = PreferencesQuestion.objects.exclude(pk__in=existing_preferences)
        new_preferences = [Preference(employee=employee, question=q) for q in missing_questions]
        Preference.objects.bulk_create(new_preferences)

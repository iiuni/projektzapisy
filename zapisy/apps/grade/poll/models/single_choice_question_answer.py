from django.db import models

from .base_answer import BaseAnswer
from .single_choice_question import SingleChoiceQuestion
from .option import Option


class SingleChoiceQuestionAnswer(BaseAnswer):
    question = models.ForeignKey(
        SingleChoiceQuestion,
        verbose_name='pytanie',
        on_delete=models.CASCADE)
    option = models.ForeignKey(
        Option,
        verbose_name='odpowiedź',
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'odpowiedzi na pytania jednokrotnego wyboru'
        verbose_name = 'odpowiedź na pytanie jednokrotnego wyboru'
        app_label = 'poll'

    def __str__(self):
        return str(self.option)

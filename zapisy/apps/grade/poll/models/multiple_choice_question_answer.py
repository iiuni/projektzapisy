from django.db import models

from .base_answer import BaseAnswer
from .multiple_choice_question import MultipleChoiceQuestion
from .option import Option


class MultipleChoiceQuestionAnswer(BaseAnswer):
    question = models.ForeignKey(
        MultipleChoiceQuestion,
        verbose_name='pytanie',
        on_delete=models.CASCADE)
    options = models.ManyToManyField(Option, verbose_name='odpowiedzi', blank=True)
    other = models.CharField(max_length=100, verbose_name='inne', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'odpowiedzi na pytania wielokrotnego wyboru'
        verbose_name = 'odpowiedź na pytanie wielokrotnego wyboru'
        app_label = 'poll'

    def __str__(self):
        ans = ""
        for option in self.options.all():
            ans += str(option) + '; '
        if self.other:
            ans += str(self.other)
        else:
            ans = ans[:-2]
        return ans

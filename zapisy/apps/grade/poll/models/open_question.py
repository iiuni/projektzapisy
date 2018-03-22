from django.db import models

from .base_question import BaseQuestion
from .saved_ticket import SavedTicket


class OpenQuestion(BaseQuestion):
    sections = models.ManyToManyField('Section',
                                      verbose_name='sekcje',
                                      through='OpenQuestionOrdering')

    class Meta:
        abstract = False
        verbose_name = 'pytanie otwarte'
        verbose_name_plural = 'pytania otwarte'
        app_label = 'poll'

    def get_all_answers_from_poll(self, poll, section):
        sts = SavedTicket.objects.filter(poll=poll)
        result = []
        for st in sts:
            result += st.openquestionanswer_set.filter(question=self,
                                                       section=section).order_by('time')
        return self, result

    def get_all_answers_from_poll_for_ticket(self, poll, section, ticket):
        result = []
        result += ticket.openquestionanswer_set.filter(question=self, section=section)
        return self, result


class OpenQuestionOrdering(models.Model):
    question = models.ForeignKey(OpenQuestion, verbose_name='pytanie', on_delete=models.CASCADE)
    sections = models.ForeignKey('Section', verbose_name='sekcja', on_delete=models.CASCADE)
    position = models.IntegerField(verbose_name='pozycja')

    class Meta:
        verbose_name_plural = 'pozycje pytań otwartych'
        verbose_name = 'pozycja pytań otwartych'
        ordering = ['sections', 'position']
        unique_together = ['sections', 'position']
        app_label = 'poll'

    def __str__(self):
        return str(self.position) + '[' + str(self.sections) + ']' + str(self.question)

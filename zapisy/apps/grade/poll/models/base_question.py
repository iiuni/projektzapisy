from django.db import models


class BaseQuestion(models.Model):
    content = models.CharField(max_length=250, verbose_name='treść')
    description = models.TextField(verbose_name='opis', blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.content)

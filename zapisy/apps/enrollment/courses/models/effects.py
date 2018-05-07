from django.db import models


class Effects(models.Model):
    group_name = models.CharField(max_length=250, verbose_name='grupa efektów')
    description = models.TextField(verbose_name='opis', null=True, blank=True)

    class Meta:
        verbose_name = 'Grupa Efektów'
        verbose_name_plural = 'Grupy Efektów'
        app_label = 'courses'

    def __str__(self):
        return str(self.group_name)

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'name': self.group_name,
            'description': self.description
        }

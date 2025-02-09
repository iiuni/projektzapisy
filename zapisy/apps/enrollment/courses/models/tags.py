from django.db import models


class BaseTag(models.Model):
    short_name = models.CharField(max_length=50, verbose_name='nazwa skrócona')
    full_name = models.CharField(max_length=250, verbose_name='nazwa pełna')
    description = models.TextField(verbose_name='opis')

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.short_name} ({self.full_name})"

    def serialize_for_json(self):
        return {
            'id': self.pk,
            'short_name': self.short_name,
            'full_name': self.full_name,
            'description': self.description,
        }


class ThematicTag(BaseTag):
    class Meta:
        verbose_name = 'Tag tematyczny (I st.)'
        verbose_name_plural = 'Tagi tematyczne (I st.)'
        app_label = 'courses'


class SpecialistTag(BaseTag):
    class Meta:
        verbose_name = 'Tag specjalistyczny (II st.)'
        verbose_name_plural = 'Tagi specjalistyczne (II st.)'
        app_label = 'courses'

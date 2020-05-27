from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class PriorityChoices(models.IntegerChoices):
    HIDDEN = 0, "Ukryte"
    LOW = 1, "Niskie"
    NORMAL = 2, "Normalne"
    HIGH = 3, "Wysokie"


class NewsManager(models.QuerySet):
    def published(self):
        return self.exclude(priority=PriorityChoices.HIDDEN)

    def get_page_number_by_news_id(self, news_id):
        """If news doesn't exist the first page is returned."""
        if not self.filter(pk=news_id).exists():
            return 1
        later_news = self.published().filter(pk__gte=news_id)
        count = later_news.count() or 1
        return ((count - 1) // settings.NEWS_PER_PAGE) + 1


class News(models.Model):
    title = models.CharField(max_length=255, verbose_name='Tytuł')
    body = models.TextField(verbose_name='Treść', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField("priorytet",
                                                choices=PriorityChoices.choices,
                                                default=PriorityChoices.NORMAL,
                                                help_text=("""
            <dl>
            <dt>Ukryte</dt>
            <dd>Wiadomość nie zostanie opublikowana;</dd>
            <dt>Niskie</dt>
            <dd>Wiadomość zostanie opublikowana na stronie, ale powiadomienia
            nie będą wysłane;
            <dt>Normalne</dt>
            <dd>Powiadomienia będą wysłane zgodnie z preferencjami użytkowników</dd>
            <dt>Wysokie</dt>
            <dd>Powiadomienia otrzymają wszyscy aktywni studenci niezależnie od
            swoich preferencji.</dd>
            <dl>
            <b>Uwaga:</b> Powiadomienia są wysyłane tylko dla nowych ogłoszeń,
            nie dla zmodyfikowanych.
        """))

    objects = NewsManager.as_manager()

    def is_published(self):
        return self.priority != PriorityChoices.HIDDEN

    class Meta:
        get_latest_by = 'date'
        ordering = ['-date', '-id']
        verbose_name = 'Ogłoszenie'
        verbose_name_plural = 'Ogłoszenia'

    def __str__(self):
        return self.title

# -*- coding: utf-8 -*-

"""
    News models
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from datetime import datetime, timedelta
from apps.notifications.models import Notification

class NewsManager(models.Manager):
    """
        News management
    """
    def new(self, category):
        """
            Returns news marked as new
        """
        if self.count_new(category) >= 3:
            begin = datetime.now() - timedelta(days=7)
            return self.category(category).filter(date__gte=begin)
        else:
            return self.get_successive_news(category, 0, 3)

    def count_new(self, category):
        """
            Returns number of news marked as new
        """
        begin = datetime.now() - timedelta(days=7)
        return self.category(category).filter(date__gte=begin).count()

    def get_successive_news(self, category, beginwith, quantity=1):
        """
            Get a number of news
        """
        return self.category(category)[beginwith:(beginwith+quantity)]

    def get_page_number_by_news_id(self, news_id):
        """
            If news doesn\'t exist the first page is returned
        """
	ids = self.get_published().values_list('id').filter(pk__gte=news_id).order_by('-id')
        if not ids.filter(pk=news_id).exists():
            return 1
        return ((ids.count()-1)/settings.NEWS_PER_PAGE) + 1

    def get_published(self):
        """
            Returns only published
        """
        return self.exclude(category='-')

    def category(self, category):
        """
            Return news tagged with a given tag.
        """
        return self.filter(category = category)
# suggested news items categories - not enforced
CATEGORIES = (
    ('-', 'Hidden'),
    ('offer', 'Oferta'),
    ('enrollment', 'Zapisy'),
    ('grade', 'Ocena zajęć'),
)

class News(models.Model):
    """
        Single news
    """
    title = models.CharField(max_length=255,
                             verbose_name=u'Tytuł')
    body = models.TextField(verbose_name=u'Treść',
                            blank=True)
    date = models.DateTimeField(default=datetime.now)
    author = models.ForeignKey(User)
    category = models.CharField(max_length=15,
                                verbose_name=u'Kategoria',
                                choices=CATEGORIES,
                                default='-')

    objects = NewsManager()

    def save(self, *args, **kwargs):
        try:
            old = News.objects.get(pk=self.pk)
        except News.DoesNotExist:
            old = None

        super(News, self).save(*args, **kwargs)

        if self.is_published() and (old and not old.is_published() or not old):
            Notification.send_notifications('send-news', {'news_id': self.pk, 'include_direct_link': True, 'subject': self.title, 'body': self.body})

    def is_published(self):
        return self.category != '-'

    class Meta:
        get_latest_by = 'date'
        ordering = ['-date', '-id']
        verbose_name = u'Ogłoszenie'
        verbose_name_plural = u'Ogłoszenia'

    def __unicode__(self):
        return self.title

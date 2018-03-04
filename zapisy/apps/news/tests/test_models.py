# -*- coding: utf-8 -*-
from random import randint

from django.test import TestCase

from datetime import datetime, timedelta

from apps.news.models import News
from utils import generate_random_news


class NewsModelTest(TestCase):
    def test_creating_news(self):
        n1 = News(title="news test", body="news body")
        self.assertEquals(str(n1), "news test")


class NewsManagerTest(TestCase):
    def test_new(self):
        (new, old, ns) = generate_random_news('-')

        nss = [o.id for o in News.objects.new('-')]
        ncs = [o.id for o in sorted(ns, key=(lambda o: o.date), reverse=True)[0:max(new, 3)]]

        self.assertEquals(nss, ncs)
        for n in ns:
            n.delete()

    def test_count_new(self):
        self.assertEquals(0, News.objects.count_new('-'))
        (new, old, ns) = generate_random_news('-')
        self.assertEquals(new, News.objects.count_new('-'))
        for n in ns:
            n.delete()

    def test_get_successive_news(self):
        ns = []
        for i in xrange(12):
            n = News(title="news", body="news body", author_id=1,
                     date=datetime.now() - timedelta(days=12 - i))
            n.save()
            ns.append(n)
        self.assertEquals(0, len(News.objects.get_successive_news('-', 0, 0)))
        self.assertEquals(0, len(
            News.objects.get_successive_news('-', randint(0, 11), 0)))
        self.assertEquals(12, len(
            News.objects.get_successive_news('-', 0, 20)))
        nss = News.objects.get_successive_news('-', 3, 6)
        for i in xrange(0, 6):
            self.assertEquals(nss[i].id, ns[8 - i].id)
        for n in ns:
            n.delete()

    def test_get_page_number_by_news_id(self):
        (news, old, ns) = generate_random_news('1', 42, 0)
        ids = [x.id for x in ns]
        range_min, range_max = min(ids), max(ids)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_max), 1)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_max - 14), 1)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_max - 15), 2)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_min + 20), 2)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_min + 15), 2)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_min), 3)
        self.assertEquals(News.objects.get_page_number_by_news_id(-1024), 1)
        self.assertEquals(News.objects.get_page_number_by_news_id(2137), 1)

        for n in ns:
            n.delete()

        (news_unpublished, old_unpublished, ns) = generate_random_news('-', 50, 0)
        ids = [x.id for x in ns]
        range_min, range_max = min(ids), max(ids)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_max), 1)
        self.assertEquals(News.objects.get_page_number_by_news_id(range_min), 1)

        for n in ns:
            n.delete()

    def test_count_new_categories(self):
        (new1, old1, ns1) = generate_random_news('1')
        (new2, old2, ns2) = generate_random_news('2')
        self.assertEquals(new1, News.objects.count_new('1'))
        self.assertEquals(new2, News.objects.count_new('2'))
        for n in ns1 + ns2:
            n.delete()

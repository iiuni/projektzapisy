# -*- coding: utf-8 -*-

from django.test import TestCase

from .utils import generate_random_news

from apps.news.templatetags.news_extras import *

class NewsTagsTest(TestCase):
    def test_newscount(self):
        (new1, old1, ns1) = generate_random_news('1')
        (new2, old2, ns2) = generate_random_news('2')        
        self.assertEqual(str(new1), newscount('1'))
        self.assertEqual(str(new2), newscount('2'))
        for n in ns1 + ns2:
            n.delete()

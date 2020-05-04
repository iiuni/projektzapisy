from django.test import TestCase

from apps.news.models import News

from .utils import generate_random_news


class NewsModelTest(TestCase):
    def test_creating_news(self):
        n1 = News(title="news test", body="news body")
        self.assertEqual(str(n1), "news test")


class NewsManagerTest(TestCase):

    def test_get_page_number_by_news_id(self):
        ns = generate_random_news(42)
        ids = [x.id for x in ns]
        range_min, range_max = min(ids), max(ids)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_max), 1)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_max - 14), 1)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_max - 15), 2)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_min + 20), 2)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_min + 15), 2)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_min), 3)
        self.assertEqual(News.objects.get_page_number_by_news_id(-1024), 1)
        self.assertEqual(News.objects.get_page_number_by_news_id(2137), 1)

        for n in ns:
            n.delete()

        ns = generate_random_news(50, published=False)
        ids = [x.id for x in ns]
        range_min, range_max = min(ids), max(ids)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_max), 1)
        self.assertEqual(News.objects.get_page_number_by_news_id(range_min), 1)

        for n in ns:
            n.delete()

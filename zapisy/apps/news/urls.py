from django.conf.urls import patterns, url

from apps.news.models import News

urlpatterns = patterns('apps.news.views',
    url(r'^$','all_news',name='news-all'),
    url(r'^(?P<news_id>[0-9]+)/$', 'all_news_focus_one'),
)

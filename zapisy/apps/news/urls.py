from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.all_news, name='news-all'),
    url(r'^(?P<news_id>[0-9]+)/$', views.all_news_focus_one, name='news-one'),
]

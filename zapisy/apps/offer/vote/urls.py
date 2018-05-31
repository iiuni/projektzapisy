from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.vote_main, name='vote-main'),
    url('^view$', views.vote_view, name='vote-view'),
    url('^vote$', views.vote, name='vote'),
    url('^summary$', views.vote_summary, name='vote-summary'),
    url(r'^summary/(?P<slug>[\w\-_]+)/$', views.proposal_vote_summary,
        name='proposal-vote-summary')
]

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.vote_main, name='vote-main'),
    path('view/', views.vote_view, name='vote-view'),
    path('vote/', views.vote, name='vote'),
    url('^summary$', views.vote_summary, name='vote-summary'),
    url(r'^summary/(?P<slug>[\w\-_]+)/$', views.proposal_vote_summary,
        name='proposal-vote-summary')
]

from django.conf.urls import patterns, url


urlpatterns = patterns( 'apps.offer.vote.views',
    url('^$',     'vote_main', name='vote-main' ),
    url('^view$', 'vote_view', name='vote-view'),
    url('^vote$', 'vote',      name='vote'),
    url('^summary$', 'vote_summary', name='vote-summary'),
    url('^summary/(?P<slug>[\w\-_]+)/$', 'proposal_vote_summary', name='proposal-vote-summary')
)

from django.conf.urls.defaults import *

urlpatterns = patterns( 'apps.offer.proposal.views',
    url(r'^$', 'offer', name='offer-main'),
    url(r'^/teacher$', 'proposal', name='my-proposal'),
    url(r'^/teacher/(?P<slug>[\w\-_]+)$', 'proposal', name='my-proposal-show'),
    url( '^/add$', 'proposal_edit', name='proposal-form' ),
    url( '^/manage/proposals$', 'manage', name='manage' ),
    url( '^/manage/select_for_voting$', 'select_for_voting'),
    url( '^/manage/groups$', 'all_groups'),
    url( '^/manage/groups/(?P<slug>[\w\-_]+)', 'course_groups'),
    url('^/(?P<slug>[\w\-_]+)/accept', 'proposal_accept', name='proposal-accept'),
    url('^/(?P<slug>[\w\-_]+)/review', 'proposal_for_review', name='proposal-review'),
    url('^/(?P<slug>[\w\-_]+)/edit', 'proposal_edit', name='proposal-edit'),
    url('^/(?P<slug>[\w\-_]+)', 'offer', name='offer-page'),
)

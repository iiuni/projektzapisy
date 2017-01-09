from django.conf.urls.defaults import *

urlpatterns = patterns('apps.help.views',
    url(r'^$', 'main_page', name='help'),
    #url(r'^terms/$', 'terms', name='help-terms'),
    url(r'^rules/$', 'rules', name='help-rules'),
    url(r'^enrollment/$', 'enrollment', name='help-enrollment'),
    #url(r'^grade/$', 'grade', name='help-grade'),
    #url(r'^mobile/$', 'mobile', name='help-mobile'),
    url(r'^export/$', 'export', name='help-export'),
    #url(r'^admin/$', 'admin', name='help-admin'),
    #url(r'^employee/$', 'employee', name='help-employee'),
    #url(r'^offer/$', 'offer', name='help-offer'),
    url(r'^errorpage/$', 'errorpage', name='help-errorpage'),
    url(r'^rqtestpage/$', 'rqtestpage', name='help-rqtestpage'),
)

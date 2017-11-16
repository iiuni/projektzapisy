from django.conf.urls import patterns, url

urlpatterns = patterns('apps.help.views',
    url(r'^$', 'main_page', name='help'),
    url(r'^rules/$', 'rules', name='help-rules'),
    url(r'^enrollment/$', 'enrollment', name='help-enrollment'),
    url(r'^export/$', 'export', name='help-export'),
    url(r'^errorpage/$', 'errorpage', name='help-errorpage'),
)

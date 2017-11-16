from django.conf.urls import patterns, url

# to view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = patterns('apps.offer.preferences.views',
    url(r'^$',       'view', name='prefs-default-view'),
    url(r'^save/$', 'save', name='preference-save'),
)

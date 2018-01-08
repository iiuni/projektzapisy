from django.conf.urls import url
from . import views

# to view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = [
    url(r'^$', views.view, name='prefs-default-view'),
    url(r'^save/$', views.save, name='preference-save'),
]

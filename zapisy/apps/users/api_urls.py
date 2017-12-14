from django.conf.urls import patterns, url

from apps.users.api import StudentList

urlpatterns = patterns('', url('^student/$', StudentList.as_view()))

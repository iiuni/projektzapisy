# -*- coding: utf-8 -*-

__author__ = 'maciek'


from django.conf.urls import *

urlpatterns = patterns(
    'apps.notifications.views',
    url(r'^notifications/save$', 'save', name='save'),
    url(r'^notifications$', 'index', name='index'),
    url(r'^notifications/vote_start$', 'vote_start', name='vote_start'),
    url(r'^notifications/grade_start$', 'grade_start', name='grade_start'),
    url(r'^notifications/enrollment_limit$', 'enrollment_limit', name='enrollment_limit'),
)

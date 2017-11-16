# -*- coding: utf-8 -*-
from apps.schedule.feeds import LatestEvents, LatestExams
from apps.schedule.views import ClassroomTermsAjaxView, EventsTermsAjaxView, MyScheduleAjaxView

__author__ = 'maciek'


from django.conf.urls import patterns, url

urlpatterns = patterns('apps.schedule.views',
    url(r'^classrooms$', 'classrooms', name='classrooms'),
    url(r'^classrooms/terms/(?P<year>[0-9]*)/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', 'ajax_get_terms',
                                                                                    name='ajax_get_terms'),
    url(r'^classrooms/reservation$', 'reservation', name='reservation'),
    url(r'^classrooms/reservations$', 'reservations', name='reservations'),
    url(r'^classrooms/conflicts$', 'conflicts', name='conflicts'),
    url(r'^classrooms/(?P<slug>[0-9]+)$', 'classroom', name='classroom'),
    url(r'^classrooms/ajax/(?P<slug>[0-9]+)$', ClassroomTermsAjaxView.as_view(), name='classroom_ajax'),
    url(r'^events/(?P<event_id>[0-9]+)/moderation$', 'moderation_message', name='moderation'),
    url(r'^events/(?P<event_id>[0-9]+)/message', 'message', name='message'),
    url(r'^events/(?P<event_id>[0-9]+)/interested$', 'change_interested', name='interested'),
    url(r'^events/(?P<event_id>[0-9]+)/edit$', 'edit_event', name='edit'),
    url(r'^events/(?P<event_id>[0-9]+)$', 'event', name='show'),
    url(r'^events/feed$', LatestEvents(), name='events_feed'),
    url(r'^events$', 'events', name='event_show'),
    url(r'^events/ajax$', EventsTermsAjaxView.as_view(), name='events_ajax'),
    url(r'^events/myschedule$', MyScheduleAjaxView.as_view(), name='my_schedule_ajax'),
    url(r'^events/(?P<event_id>[0-9]+)/decision$', 'decision', name='decision'),
    url(r'^events/history$', 'history', name='history'),
    url(r'^session$', 'session', name='session'),
    url(r'^session/feed$', LatestExams(), name='session_feed'),
    url(r'^session/statistics$', 'statistics', name='statistics'),
    url(r'^events/report$', 'events_report', name='events_report'),
)

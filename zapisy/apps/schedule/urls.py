from django.conf.urls import url

from . import feeds, views

urlpatterns = [
    url(r'^classrooms$', views.classrooms, name='classrooms'),
    url(r'^classrooms/get_terms/(?P<year>[0-9]*)-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})/$', views.get_terms,
        name='get_terms'),
    url(r'^classrooms/reservation$', views.new_reservation, name='reservation'),
    url(r'^classrooms/reservations$', views.reservations, name='reservations'),
    url(r'^classrooms/conflicts$', views.conflicts, name='conflicts'),
    url(r'^classrooms/(?P<slug>[0-9]+)$', views.classroom, name='classroom'),
    url(r'^classrooms/ajax/(?P<slug>[0-9]+)$', views.ClassroomTermsAjaxView.as_view(), name='classroom_ajax'),
    url(r'^events/(?P<event_id>[0-9]+)/moderation$', views.moderation_message, name='moderation'),
    url(r'^events/(?P<event_id>[0-9]+)/message', views.message, name='message'),
    url(r'^events/(?P<event_id>[0-9]+)/interested$', views.change_interested, name='interested'),
    url(r'^events/(?P<event_id>[0-9]+)/edit$', views.edit_reservation, name='edit'),
    url(r'^events/(?P<event_id>[0-9]+)$', views.event, name='show'),
    url(r'^events/feed$', feeds.LatestEvents(), name='events_feed'),
    url(r'^events$', views.events, name='event_show'),
    url(r'^events/ajax$', views.EventsTermsAjaxView.as_view(), name='events_ajax'),
    url(r'^events/myschedule$', views.MyScheduleAjaxView.as_view(), name='my_schedule_ajax'),
    url(r'^events/(?P<event_id>[0-9]+)/decision$', views.decision, name='decision'),
    url(r'^events/history$', views.history, name='history'),
    url(r'^session$', views.session, name='session'),
    url(r'^session/feed$', feeds.LatestExams(), name='session_feed'),
    url(r'^events/report$', views.events_report, name='events_report'),
]

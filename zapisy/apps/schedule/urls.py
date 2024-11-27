from django.urls import path, re_path

from . import feeds, views

urlpatterns = [
    path('classrooms/', views.classrooms, name='classrooms'),
    re_path(r'^classrooms/get_terms/(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})/$',
            views.get_terms,
            name='get_terms'),
    path('classrooms/reservation/', views.new_reservation, name='reservation'),
    path('classrooms/reservations/', views.reservations, name='reservations'),
    path('classrooms/conflicts/', views.conflicts, name='conflicts'),
    path('classrooms/<int:slug>/', views.classroom, name='classroom'),
    path('classrooms/ajax/<int:slug>/',
         views.ClassroomTermsAjaxView.as_view(),
         name='classroom_ajax'),
    path('events/<int:event_id>/moderation/', views.moderation_message, name='moderation'),
    path('events/<int:event_id>/message/', views.message, name='message'),
    path('events/<int:event_id>/interested/', views.change_interested, name='interested'),
    path('events/<int:event_id>/edit/', views.edit_reservation, name='edit'),
    path('events/<int:event_id>/', views.event, name='show'),
    path('events/feed/', feeds.LatestEvents(), name='events_feed'),
    path('events/', views.events, name='event_show'),
    path('events/ajax/', views.EventsTermsAjaxView.as_view(), name='events_ajax'),
    path('events/<int:event_id>/decision/', views.decision, name='decision'),
    path('events/history/', views.history, name='history'),
    path('session/', views.session, name='session'),
    path('session/feed/', feeds.LatestExams(), name='session_feed'),
    path('events/report/', views.events_report, name='events_report'),
    path('freedays/', views.special_days, {"day_type": "freedays"}, name='freedays'),
    path('changeddays/', views.special_days, {"day_type": "changeddays"}, name='changeddays', )
]

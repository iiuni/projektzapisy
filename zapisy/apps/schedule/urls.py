from django.urls import path

from . import views

urlpatterns = [
    path('', views.calendar, name='calendar'),
    path('report/', views.events_report, name='report'),
    path('terms/', views.terms, name="terms"),
    path('chosen-days-terms/', views.chosen_days_terms, name="chosen-days-terms"),
    path('events/', views.events, name="events"),
    path('events/<int:event_id>/', views.event, name='event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete'),
    path('check-conflicts/', views.check_conflicts, name='check-conflicts'),
    path('check-conflicts/<int:event_id>/', views.check_conflicts, name='check-conflicts-id'),
]

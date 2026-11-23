"""Enrollment actions."""

from django.urls import path

from apps.enrollment.records import views

urlpatterns = [
    path('enqueue/', views.enqueue, name='records-enqueue'),
    path('dequeue/', views.dequeue, name='records-dequeue'),
    path('pin/', views.pin, name='pin'),
    path('unpin/', views.unpin, name='unpin'),
    path('queue-set-priority/', views.queue_set_priority, name='records-set-priority'),
]

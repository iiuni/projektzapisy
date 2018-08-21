"""Enrollment actions."""

from django.urls import path
from apps.enrollment.records import views

urlpatterns = [
    path('enqueue/', views.enqueue, name='records-enqueue'),
    path('dequeue/', views.dequeue, name='records-dequeue'),
]

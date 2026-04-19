from django.urls import path

from . import views

urlpatterns = [
    path('', views.withdrawal_list, name='list'),
    path('request/', views.request_withdrawal, name='request'),
]

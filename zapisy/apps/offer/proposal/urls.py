from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.offer, name='offer-main'),
    path('add/', views.proposal_edit, name='proposal-form'),
    path('teacher/', views.my_proposals, name='my-proposals'),
    path('teacher/<slug:slug>/', views.my_proposals, name='my-proposal-show'),
    path('<slug:slug>/edit', views.proposal_edit, name='proposal-edit'),
    path('<slug:slug>/clone', views.proposal_clone, name='proposal-clone'),
    path('<slug:slug>/', views.offer, name='offer-page'),
]

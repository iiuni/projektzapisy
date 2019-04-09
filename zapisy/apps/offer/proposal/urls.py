from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.offer, name='offer-main'),
    path('add/', views.proposal_edit, name='proposal-form'),
    path('teacher/', views.my_proposals, name='my-proposals'),
    path('teacher/<slug:slug>/', views.my_proposals, name='my-proposal-show'),
    path('<slug:slug>/edit', views.proposal_edit, name='proposal-edit'),
    path('<slug:slug>/', views.offer, name='offer-page'),

    url('^manage/proposals$', views.manage, name='manage'),
    url('^manage/select_for_voting$', views.select_for_voting),
    url('^manage/groups$', views.all_groups),
    url(r'^manage/groups/(?P<slug>[\w\-_]+)', views.course_groups),
    url(r'^(?P<slug>[\w\-_]+)/accept', views.proposal_accept, name='proposal-accept'),
    url(r'^(?P<slug>[\w\-_]+)/review', views.proposal_for_review, name='proposal-review'),
]

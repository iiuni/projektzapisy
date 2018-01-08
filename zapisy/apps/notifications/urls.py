from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^notifications/save$', views.save, name='save'),
    url(r'^notifications$', views.index, name='index'),
    url(r'^notifications/vote_start$', views.vote_start,
        name='vote_start'),
    url(r'^notifications/grade_start$', views.grade_start,
        name='grade_start'),
    url(r'^notifications/enrollment_limit$', views.enrollment_limit,
        name='enrollment_limit'),
]

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w\-_]+)$', views.course, name='course-page'),
    url(r'^$', views.courses, name='course-list'),
    url(r'^$', views.courses, name='enrollment-main'),
    url(r'^get_semester_info/(?P<semester_id>\d+)$', views.get_semester_info),
]

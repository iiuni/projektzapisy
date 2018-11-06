from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[\w\-_]+)$', views.course_page, name='course-page'),
    url(r'^(?P<slug>[\w\-_]+)\.json$', views.course_ajax, name='course-page-json'),
    url(r'^$', views.courses, name='course-list'),
    url(r'^$', views.courses, name='enrollment-main'),
    url(r'^get_semester_info/(?P<semester_id>\d+)$', views.get_semester_info),
]

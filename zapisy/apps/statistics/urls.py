from django.conf.urls import url
from . import views

urlpatterns = [
    url('^students/$', views.students, name='students'),
    url('^groups/$', views.groups, name='groups'),
]

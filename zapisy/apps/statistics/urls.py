from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.main, name='main'),
    url('^students/$', views.students, name='students'),
    url('^groups/$', views.groups, name='groups'),
    url('^vote/$', views.votes, name='vote'),
    url('^swap/$', views.swap, name='swap')
]

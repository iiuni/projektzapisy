from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main_page, name='help'),
    url(r'^rules/$', views.rules, name='help-rules'),
    url(r'^enrollment/$', views.enrollment, name='help-enrollment'),
    url(r'^export/$', views.export, name='help-export'),
    url(r'^errorpage/$', views.errorpage, name='help-errorpage'),
]

from django.conf.urls import url
from . import views

app_name = "notifications"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^preferences/$', views.preferences, name='preferences'),
    url(r'^preferences/save$', views.preferences_save, name='preferences-save'),
]

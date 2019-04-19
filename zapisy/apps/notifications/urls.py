from django.conf.urls import url
from . import views

app_name = "notifications"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get$', views.get_notifications, name='get_notifications'),
    url(r'^count$', views.get_counter, name='get_counter'),
    url(r'^delete/all$', views.deleteAll, name='delete-all-notifications'),
    url(r'^preferences/$', views.preferences, name='preferences'),
    url(r'^preferences/save$', views.preferences_save, name='preferences-save'),
]

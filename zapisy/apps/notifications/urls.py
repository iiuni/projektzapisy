from django.conf.urls import url
from . import views

# Urls: "get", "count", "delete" and "delete/all" 
# are in charge of manage notifications in Widget.vue

app_name = "notifications"
urlpatterns = [
    url(r'^get$', views.get_notifications, name='get_notifications'),
    url(r'^count$', views.get_counter, name='get_counter'),
    url(r'^delete$', views.deleteOne, name='delete-one-notification'),
    url(r'^delete/all$', views.deleteAll, name='delete-all-notifications'),
    url(r'^preferences/$', views.preferences, name='preferences'),
    url(r'^preferences/save$', views.preferences_save, name='preferences-save'),
]

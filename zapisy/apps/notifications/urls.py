from django.urls import path
from . import views

# Urls: "get", "count", "delete" and "delete/all"
# are in charge of manage notifications in Widget.vue

app_name = "notifications"
urlpatterns = [
    path('get', views.get_notifications, name='get_notifications'),
    path('count', views.get_counter, name='get_counter'),
    path('delete', views.delete_one, name='delete-one-notification'),
    path('delete/all', views.delete_all, name='delete-all-notifications'),
    path('preferences/save', views.preferences_save, name='preferences-save'),
]

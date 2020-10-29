from django.urls import path

from . import views

urlpatterns = [
    path('change/', views.change_desiderata, name='change_desiderata'),
]

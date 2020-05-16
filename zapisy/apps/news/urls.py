from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_news, name='news-all'),
    path('<int:news_id>', views.all_news_focus_one, name='news-one'),
]

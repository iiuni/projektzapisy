from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.list_all, name="main"),
    path("<int:id>", views.view_thesis, name="selected_thesis"),
    path('<int:id>/edit', views.edit_thesis, name='edit_thesis'),
    path("new", views.new_thesis, name="new_thesis"),
    path('<int:id>/vote', views.vote_for_thesis, name="vote_thesis"),
    path('<int:id>/remark', views.edit_remark, name="remark_thesis"),
    path('<int:id>/form/<int:studentid>', views.gen_form, name="gen_form"),
    path('<int:id>/rejecter', views.rejecter_decision, name="rejecter_thesis"),
    path('<int:id>/delete', views.delete_thesis, name="delete_thesis"),
]

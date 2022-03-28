from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('new', views.add_defect, name='new'),
    path('<int:defect_id>', views.show_defect, name='show_defect'),
    path('<int:defect_id>/edit', views.edit_defect, name='edit_defect'),
    path('delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('<int:defect_id>/edit-repair-info', views.post_information_from_repairer, name='repair_info')
]

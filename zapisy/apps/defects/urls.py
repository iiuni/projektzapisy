from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='main'),
    path('print', views.print_defects, name="print"),
    re_path(r'^print/(?P<defects_ids>(\d+,)*\d+)/$', views.print_defects, name="print_list"),
    path('new', views.add_defect, name='new'),
    path('delete', views.delete_defects_endpoint, name='delete'),
    path('<int:defect_id>', views.show_defect, name='show_defect'),
    path('<int:defect_id>/edit', views.edit_defect, name='edit_defect'),
    path('<int:defect_id>/delete', views.delete_defect, name='delete_defect'),
    path('delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('<int:defect_id>/edit-repair-info', views.post_information_from_defect_manager, name='repair_info')
]
from django.urls import path

from apps.enrollment.timetable import views

urlpatterns = [
    path('', views.my_timetable, name='my-timetable'),
    path('prototype/', views.my_prototype, name='my-prototype'),
    path('prototype/action/<int:group_id>/', views.prototype_action, name='prototype-action'),
    path('prototype/course/<int:course_id>/', views.prototype_get_course, name='prototype-get-course'),
    path('prototype/update/', views.prototype_update_groups, name='prototype-update'),
    path('calendar-export/', views.calendar_export, name='calendar-export')
]

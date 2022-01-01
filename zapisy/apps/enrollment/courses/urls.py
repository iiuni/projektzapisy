"""Views for presenting courses groups and records in different ways.

The separation of concerns between courses and records app is natural. The
courses app will be responsible for presenting the courses and groups in
different ways: in the course view, student's schedule and schedule prototype.
The records app will only be responsible for basic actions and will be kept
minimal.
"""
from django.urls import path

from apps.enrollment.courses import views

urlpatterns = [
    path('', views.courses_list, name='course-list'),
    path('<slug:slug>', views.course_view, name='course-page'),
    path('<slug:course_slug>/list', views.course_list_view, name='course-student-list'),
    path('<slug:course_slug>/<int:class_type>/list', views.course_list_view, name='class-type-student-list'),
    path('semester/<int:semester_id>', views.courses_list, name='courses-semester'),
    path('group/<int:group_id>', views.group_view, name='group-view'),
    path('group/<int:group_id>/group/csv', views.group_enrolled_csv, name='group-csv'),
    path('group/<int:group_id>/queue/csv', views.group_queue_csv, name='queue-csv'),
    path('course/<slug:course_slug>/course/csv', views.course_enrolled_csv, name='course-csv'),
    path('course/<slug:course_slug>/queue/csv', views.course_queue_csv, name='course-queue-csv'),

]

"""Views for presenting courses groups and records in different ways.

The separation of concerns between courses and records app is natural. The
courses app will be responsible for presenting the courses and groups in
different ways: in the course view, student's schedule and schedule prototype.
The records app will only be responsible for basic actions and will be kept
minimal.
"""
from django.urls import path

from apps.enrollment.courses.views import (
    CoursesListView, CourseDetailView, CourseStudentListView,
    group_view,
    group_enrolled_csv, group_queue_csv, course_enrolled_csv, course_queue_csv,
)

urlpatterns = [
    path('', CoursesListView.as_view(), name='course-list'),
    path('<slug:slug>', CourseDetailView.as_view(), name='course-page'),
    path('<slug:course_slug>/list', CourseStudentListView.as_view(), name='course-student-list'),
    path('<slug:course_slug>/<int:class_type>/list', CourseStudentListView.as_view(), name='class-type-student-list'),
    path('semester/<int:semester_id>', CoursesListView.as_view(), name='courses-semester'),
    path('group/<int:group_id>', group_view, name='group-view'),
    path('group/<int:group_id>/group/csv', group_enrolled_csv, name='group-csv'),
    path('group/<int:group_id>/queue/csv', group_queue_csv, name='queue-csv'),
    path('course/<slug:course_slug>/course/csv', course_enrolled_csv, name='course-csv'),
    path('course/<slug:course_slug>/queue/csv', course_queue_csv, name='course-queue-csv'),
]

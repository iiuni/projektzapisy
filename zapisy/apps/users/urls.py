from django.urls import path

from . import views

urlpatterns = [
    path('', views.my_profile, name='my-profile'),
    path('email-change/', views.email_change, name='email-change'),
    path('employee-data-change/', views.employee_data_change, name='employee-data-change'),
    path('employees/', views.employees_view, name='employees-list'),
    path('students/', views.students_view, name='students-list'),
    path('employees/<int:user_id>/', views.employees_view, name='employee-profile'),
    path('students/<int:user_id>/', views.students_view, name='student-profile'),
    path('personal-data-consent/', views.personal_data_consent, name='personal_data_consent'),
]

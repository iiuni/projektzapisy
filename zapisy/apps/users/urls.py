from typing import List, Union, Any
from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url('^login/$', views.login_plus_remember_me, {'template_name': 'users/login.html'}, name='user-login'),
    url('^$', views.my_profile, name='my-profile'),
    url('^email-change/$', views.email_change, name='email-change'),
    url('^setlang/$', views.set_language, name='setlang'),
    url('^employee-data-change/$', views.consultations_change, name='consultations-change'),
    url('^logout/$', views.cas_logout, name='user-logout'),
    path('employees/', views.employees_view, name='employees-list'),
    path('students/', views.students_view, name='students-list'),
    path('employees/<int:user_id>/', views.employees_view, name='employee-profile'),
    path('students/<int:user_id>/', views.students_view, name='student-profile'),
    url('^ical/$', views.create_ical_file, name='ical'),
    url('^personal-data-consent/$', views.personal_data_consent, name='personal_data_consent')
]

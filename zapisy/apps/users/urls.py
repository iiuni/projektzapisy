from typing import List, Union, Any
from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.login_plus_remember_me, {'template_name': 'users/login.html'}, name='user-login'),
    url('^$', views.my_profile, name='my-profile'),
    url('^email-change/$', views.email_change, name='email-change'),
    url('^setlang/$', views.set_language, name='setlang'),
    url('^employee-data-change/$', views.consultations_change, name='consultations-change'),
    url('^logout/$', views.cas_logout, name='user-logout'),
    url('^employees/$', views.employees_view, name='employees-list'),
    url('^students/$', views.students_view, name='students-list'),
    url(r'^employees/(?P<user_id>(\d+))?$', views.employees_view, name='employee-profile'),
    url(r'^students/(?P<user_id>(\d+))?$', views.students_view, name='student-profile'),
    url('^ical/$', views.create_ical_file, name='ical'),
    url('^email-students/$', views.email_students, name='email-students'),
    url('^personal-data-consent/$', views.personal_data_consent, name='personal_data_consent')
]

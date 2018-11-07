from typing import List, Union, Any
from django.conf.urls import url
from django.contrib.auth.views import password_reset, password_reset_confirm, \
    password_reset_complete, password_reset_done, PasswordChangeView
from . import views

urlpatterns = [
    url('^login/$', views.login_plus_remember_me, {'template_name': 'users/login.html'}, name='user-login'),
    url(r'^profile/employee/(?P<user_id>(\d+))?$', views.employee_profile, name='employee-profile'),
    url(r'^profile/student/(?P<user_id>(\d+))?$', views.student_profile, name='student-profile'),
    url('^$', views.my_profile, name='my-profile'),
    url('^email-change/$', views.email_change, name='email-change'),
    url('^setlang/$', views.set_language, name='setlang'),
    url('^employee-data-change/$', views.consultations_change, name='consultations-change'),
    url('^password-change/$', PasswordChangeView.as_view(template_name='users/password_change_form.html'),
        name='password_change'),
    url('^password-change-done/$', views.password_change_done, name='password_change_done'),
    url('^password-reset/$', password_reset, {'template_name': 'users/password_reset_form.html'}, name='password_reset'),
    url('^password-reset-done/$', password_reset_done, {'template_name': 'users/password_reset_done.html'}, name='password_reset_done'),
    url(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm, {'template_name': 'users/password_reset_confirm.html'}, name='password_reset_confirm'),
    url('^password-reset-complete/$', password_reset_complete, {'template_name': 'users/password_reset_complete.html'}, name='password_reset_complete'),
    url('^logout/$', views.logout, name='user-logout'),
    url('^employees/$', views.employees_list, name='employees-list'),
    url('^students/$', views.students_list, name='students-list'),
    url('^students/(?P<begin>[A-Z]|(All))/$', views.students_list, name='students-char-list'),
    url('^employees/(?P<begin>[A-Z]|(All))/$', views.employees_list, name='employees-char-list'),
    url('^ical/$', views.create_ical_file, name='ical'),
    url('^email-students/$', views.email_students, name='email-students'),
    url('^personal-data-consent/$', views.personal_data_consent, name='personal_data_consent')
]

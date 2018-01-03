# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.views import login, logout

import os

urlpatterns = [
    #MAIN PAGE
    url('login/', login, {'template_name': 'mobile/login.html'}),
    url('^logout/$', logout, {'template_name': 'mobile/logout.html'}, name='user-mobile-logout'),
    url('^$', 'apps.mobile.views.main_page', name='main-page'),
    url(r'^nomobile/$', 'apps.mobile.views.noMobile', name = 'no-mobile'),
    url(r'^enrollment/$', 'apps.mobile.views.studentCourseList', name = 'student-enrollment'),
    url(r'^enrollment/other/', 'apps.mobile.views.otherCourses', name = 'enrollment-other'),
    #STUDENT-SCHEDULE
    url(r'records/schedule/$', 'apps.mobile.views.studentSchedule', name = 'student-schedule'),
    url(r'records/schedule/(?P<schedule_owner>\w+)/$', 'apps.mobile.views.studentSchedule', name = 'student-schedule-owner'),
    url(r'records/schedule/(?P<schedule_owner>\w+)/(?P<delta>\-?\d+)/$', 'apps.mobile.views.studentSchedule', name = 'student-schedule-delta'),
    
    url(r'employees/$', 'apps.mobile.views.employeesList', name = 'employees-list'),
    url(r'employees/(?P<key>\d)$', 'apps.mobile.views.employeesList', name = 'employees-list'),
    
    url(r'employees/schedule/(?P<schedule_owner>\w+)/$', 'apps.mobile.views.employeeSchedule', name = 'employee-schedule-owner'),
    url(r'employees/schedule/(?P<schedule_owner>\w+)/(?P<delta>\-?\d+)/$', 'apps.mobile.views.employeeSchedule', name = 'employee-schedule-delta'),
    
    url(r'students/$', 'apps.mobile.views.studentsList', name = 'students-list'),
    url(r'students/(?P<key>\d)$', 'apps.mobile.views.studentsList', name = 'students-list'),
    
    
    url(r'^(?P<cat>[\w\-_]+)/$', 'apps.news.views.latest_news', name='latest_news'),
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    url(r'^course/(?P<slug>[\w\-_]+)', 'apps.mobile.views.courseTerms', name='course-terms'),
    (r'^group/(?P<group_id>\d+)/assign/$', 'apps.mobile.views.assign'),
    (r'^group/(?P<group_id>\d+)/resign/$', 'apps.mobile.views.resign'),
    (r'^group/(?P<group_from>\d+)/(?P<group_to>\d+)/reassign/$', 'apps.mobile.views.reassign'),
]

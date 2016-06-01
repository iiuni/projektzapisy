# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

from django.contrib import admin
import os
import settings

admin.autodiscover()

from feeds import LatestNews


urlpatterns = patterns('',
    #MAIN PAGE
    url('^$', 'apps.news.views.main_page', name='main-page'),
    #HELP
    (r'^help/', include('apps.help.urls')),
    #Z
    #url('^enrollment/$', 'apps.enrollment.courses.views.main', name='enrollment-main'),
    (r'^courses/', include('apps.enrollment.courses.urls')),
    (r'^records/', include('apps.enrollment.records.urls')),
    (r'^statistics/', include('apps.statistics.urls', namespace='statistics')),
    url(r'^consultations/$', 'apps.users.views.consultations_list', name="consultations-list"),

    (r'^news/', include('apps.news.urls')),
    (r'^jstests/', 'django.views.generic.simple.direct_to_template', {'template': 'jstests/tests.html'}),
    (r'^users/', include('apps.users.urls')),
    ('accounts/', include('apps.email_change.urls')),

    (r'^grade/', include('apps.grade.urls')),
#    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    (r'^feeds/news/$', LatestNews()),
    url(r'^s/(?P<query>.*)/$', 'apps.users.views.students_list', name='users-list-search'),
    url(r'^e/(?P<query>.*)/$', 'apps.users.views.employees_list', name='users-list-search'),

    (r'^fereol_admin/courses/import_semester', 'apps.enrollment.courses.admin.views.import_semester'),
    (r'^fereol_admin/courses/import_schedule', 'apps.enrollment.courses.admin.views.import_schedule'),
    (r'^fereol_admin/courses/refresh_semester', 'apps.enrollment.courses.admin.views.refresh_semester'),
    url(r'^fereol_admin/courses/group/change_limit', 'apps.enrollment.courses.admin.views.change_group_limit', name='change-group-limit'),
    (r'^fereol_admin/courses/group/remove_student', 'apps.enrollment.courses.admin.views.remove_student'),
    (r'^fereol_admin/courses/group/add_student', 'apps.enrollment.courses.admin.views.add_student'),
    (r'^fereol_admin/courses/finish_schedule_import', 'apps.enrollment.courses.admin.views.finish_import_schedule'),
    (r'^fereol_admin/users/export_zamawiani', 'apps.users.admin.views.export_zamawiani'),
    (r'^fereol_admin/users/import_zamawiani', 'apps.users.admin.views.import_zamawiani'),
    (r'^fereol_admin/users/import_new_zamawiani', 'apps.users.admin.views.import_new_zamawiani'),
    (r'^offer', include('apps.offer.proposal.urls')),
    (r'^prefs/', include('apps.offer.preferences.urls')),
    (r'^desiderata', include('apps.offer.desiderata.urls')),
    (r'^', include('apps.schedule.urls', namespace='events')),
    (r'^', include('apps.notifications.urls', namespace='notifications')),
    (r'^vote/', include('apps.offer.vote.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^fereol_admin/', include(admin.site.urls)),

)


if not settings.RELEASE:
    urlpatterns += patterns('',
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    (r'^vote/', include('apps.offer.vote.urls')),
    # OD
    #url('^offer/$', 'apps.offer.proposal.views.main', name='offer-main'),
    # OCENA ZAJĘĆ

    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')})

    #

    #CHANGE TO apps.mobile
    #url(r'^mobile/$', 'apps.mobile.views.onMobile', name = 'on-mobile'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),


)


import os
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from apps.feeds import LatestNews
import apps.news.views
from apps.users import views as users_views
from apps.enrollment.courses.admin import views as courses_admin_views
from apps.enrollment.courses.rest_api import semester_api
from django_cas_ng import views
from rest_framework import routers

admin.autodiscover()
router = routers.DefaultRouter()
router.register(r'semesters', semester_api.SemesterViewSet)


urlpatterns = [
    url('^$', apps.news.views.main_page, name='main-page'),
    url(r'^api/', include(router.urls)),
    url(r'^help/', include('apps.help.urls')),
    url(r'^courses/', include('apps.enrollment.courses.urls')),
    url(r'^records/', include('apps.enrollment.records.urls')),
    url(r'^statistics/', include('apps.statistics.urls', namespace='statistics')),
    url(r'^consultations/$', users_views.consultations_list, name="consultations-list"),

    url(r'^news/', include('apps.news.urls')),
    url(r'^jstests/', TemplateView.as_view(template_name="jstests/tests.html")),
    url(r'^users/', include('apps.users.urls')),
    url('accounts/', include('apps.email_change.urls')),

    url(r'^grade/', include('apps.grade.urls')),
    url(r'^feeds/news/$', LatestNews()),
    url(r'^s/(?P<query>.*)/$', users_views.students_list, name='users-list-search'),
    url(r'^e/(?P<query>.*)/$', users_views.employees_list, name='users-list-search'),

    url(r'^fereol_admin/courses/import_semester', courses_admin_views.import_semester),
    url(r'^fereol_admin/courses/import_schedule', courses_admin_views.import_schedule),
    url(r'^fereol_admin/courses/refresh_semester', courses_admin_views.refresh_semester),
    url(r'^fereol_admin/courses/group/change_limit', courses_admin_views.change_group_limit, name='change-group-limit'),
    url(r'^fereol_admin/courses/group/remove_student', courses_admin_views.remove_student),
    url(r'^fereol_admin/courses/group/add_student', courses_admin_views.add_student),
    url(r'^offer/', include('apps.offer.proposal.urls')),
    url(r'^prefs/', include('apps.offer.preferences.urls')),
    url(r'^desiderata/', include('apps.offer.desiderata.urls')),
    url(r'^', include('apps.schedule.urls', namespace='events')),
    url(r'^', include('apps.notifications.urls', namespace='notifications')),
    url(r'^vote/', include('apps.offer.vote.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^fereol_admin/', include(admin.site.urls)),
    url(r'^accounts/login$', views.login, name='cas_ng_login'),
    url(r'^accounts/logout$', views.logout, name='cas_ng_logout'),
    url(r'^accounts/callback$', views.callback, name='cas_ng_proxy_callback'),
]

"""
if not settings.RELEASE:
    urlpatterns += [
    url(r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    url(r'^vote/', include('apps.offer.vote.urls')),
    # OD
    #url('^offer/$', 'apps.offer.proposal.views.main', name='offer-main'),
    # OCENA ZAJĘĆ

    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static')})

    #

    #CHANGE TO apps.mobile
    #url(r'^mobile/$', 'apps.mobile.views.onMobile', name = 'on-mobile'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
]
"""

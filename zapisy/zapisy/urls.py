from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django_cas_ng import views as cas_views

import apps.news.views
from apps.api.rest.v1.urls import router as api_router_v1
from apps.feeds import LatestNews
from apps.users import views as users_views

admin.autodiscover()

urlpatterns = [
    url('^$', apps.news.views.main_page, name='main-page'),
    url(r'^api/v1/', include(api_router_v1.urls)),
    url(r'^help/', include('apps.help.urls')),
    url(r'^courses/', include('apps.enrollment.courses.urls')),
    url(r'^records/', include('apps.enrollment.records.urls')),
    path('timetable/', include('apps.enrollment.timetable.urls')),
    url(r'^statistics/', include(('apps.statistics.urls', 'statistics'), namespace='statistics')),
    url(r'^consultations/$', users_views.consultations_list, name="consultations-list"),
    path('theses/', include(('apps.theses.urls', 'theses'), namespace='theses')),

    url(r'^news/', include('apps.news.urls')),
    url(r'^users/', include('apps.users.urls')),

    url(r'^grade/', include('apps.grade.urls')),
    url(r'^feeds/news/$', LatestNews()),
    url(r'^s/(?P<query>.*)/$', users_views.students_list, name='users-list-search'),
    url(r'^e/(?P<query>.*)/$', users_views.employees_list, name='users-list-search'),

    url(r'^offer/', include('apps.offer.proposal.urls')),
    url(r'^prefs/', include('apps.offer.preferences.urls')),
    url(r'^desiderata/', include('apps.offer.desiderata.urls')),
    url(r'^', include(('apps.schedule.urls', 'events'), namespace='events')),
    url(r'^vote/', include('apps.offer.vote.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^fereol_admin/', admin.site.urls),


    path('accounts/', include('apps.email_change.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout', users_views.cas_logout, name='cas_ng_logout'),
    path('accounts/callback', cas_views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
]

urlpatterns += [
    path('django-rq/', include('django_rq.urls')),
    path('notifications/', include('apps.notifications.urls')),
]

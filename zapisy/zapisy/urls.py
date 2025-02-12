from django.contrib import admin
from django.urls import include, path
from django_cas_ng import views as cas_views

import apps.news.views
from apps.api.rest.v1.urls import router as api_router_v1
from apps.users.views import CustomLoginView, CustomLogoutView

admin.autodiscover()

urlpatterns = [
    path('', apps.news.views.main_page, name='main-page'),
    path('api/v1/', include(api_router_v1.urls)),
    path('close/', apps.news.views.close_page, name='close-page'),
    path('courses/', include('apps.enrollment.courses.urls')),
    path('records/', include('apps.enrollment.records.urls')),
    path('timetable/', include('apps.enrollment.timetable.urls')),
    path('grade/', include('apps.grade.urls')),
    path('news/', include('apps.news.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('offer/', include('apps.offer.urls')),
    path('statistics/', include(('apps.statistics.urls', 'statistics'), namespace='statistics')),
    path('theses/', include(('apps.theses.urls', 'theses'), namespace='theses')),
    path('users/', include('apps.users.urls')),
    path('', include(('apps.schedule.urls', 'events'), namespace='events')),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('fereol_admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login', CustomLoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout', CustomLogoutView.as_view(), name='cas_ng_logout'),
    path('accounts/callback', cas_views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
]

from django.conf.urls import patterns, url

urlpatterns = patterns( 'apps.enrollment.courses.views',
    url('^(?P<slug>[\w\-_]+)$', 'course', name='course-page'),
    url('^$', 'courses',  name='course-list'),
    url('^$', 'courses',  name='enrollment-main'),
    url('^get_semester_info/(?P<semester_id>\d+)$', 'get_semester_info'),
)

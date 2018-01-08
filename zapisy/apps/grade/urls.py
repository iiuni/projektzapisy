from django.conf.urls import include, url
from .poll import views as poll_views

# to tree/list_view and description, pass by GET:
# format=json - returns data as json
# format=html - returns data rendered with template, not using the base template
# by default, they return a fully rendered page

urlpatterns = [
    url(r'^$', poll_views.main, name='grade-main'),
    url(r'^enable_grade$', poll_views.enable_grade, name='grade-enable-grade'),
    url(r'^disable_grade$', poll_views.disable_grade, name='grade-disable-grade'),
    
    url(r'^grade_logout$', poll_views.grade_logout, name='grade-logout'),
    
    url(r'^poll/', include('apps.grade.poll.urls')),
    url(r'^ticket/', include('apps.grade.ticket_create.urls')),
]

from django.conf.urls import url
from apps.users.api import StudentList

urlpatterns = [
    url('^student/$', StudentList.as_view())
]

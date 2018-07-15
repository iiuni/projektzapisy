from typing import List, Union, Any
from django.conf.urls import url
from django.urls.resolvers import RegexURLPattern, RegexURLResolver
from apps.users.api import StudentList


urlpatterns: List[Union[Union[RegexURLResolver, RegexURLPattern], Any]] = [
    url('^student/$', StudentList.as_view())
]

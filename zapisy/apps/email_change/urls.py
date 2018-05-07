#  This file is part of django-email-change.
#
#  django-email-change adds support for email address change and confirmation.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-email-change
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-email-change
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^email/change/$', views.email_change_view, name='email_change'),
    url(r'^email/verification/sent/$',
        TemplateView.as_view(template_name="email_change/email_verification_sent.html")),
    # Note taken from django-registration
    # Verification keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad verification key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^email/verify/(?P<verification_key>\w+)/$', views.email_verify_view, name='email_verify'),
    url(r'^email/change/complete/$',
        TemplateView.as_view(template_name="email_change/email_change_complete.html")),
]

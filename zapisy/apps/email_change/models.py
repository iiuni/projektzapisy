#
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

import datetime

from django.db import models

from apps.email_change import settings


class EmailChangeRequest(models.Model):
    user = models.OneToOneField('auth.User', related_name='%(class)s_user',
                                on_delete=models.CASCADE)
    verification_key = models.CharField(max_length=40)
    email = models.EmailField(max_length=75)    # Contains the new email address
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'email change request'
        verbose_name_plural = 'email change requests'

    def __str__(self):
        return '(%s) %s --> %s' % (self.user.username, self.user.email, self.email)

    def has_expired(self):
        dt = datetime.timedelta(days=settings.EMAIL_CHANGE_VERIFICATION_DAYS)
        expiration_date = self.date_created + dt
        return expiration_date <= datetime.datetime.now()

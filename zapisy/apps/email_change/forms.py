# -*- coding: utf-8 -*-
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

from django import forms
from django.contrib.auth.models import User


class EmailChangeForm(forms.ModelForm):

    class Meta:
        fields = ['email']
        model = User

    email = forms.EmailField(label="adres email", max_length=75)

    def __init__(self, *args, **kwargs):
        super(EmailChangeForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'placeholder': self.instance.email,
        })

    def clean_email(self):
        """
        Checks whether the new email address differs from the user's current
        email address.
        """

        email = self.cleaned_data.get('email')

        if self.instance.email == email:
            raise forms.ValidationError('New email address cannot be the same \
                as your current email address')

        return email

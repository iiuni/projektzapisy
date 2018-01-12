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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.apps import apps
from django.template.loader import render_to_string
from django.core.mail import send_mail

from apps.email_change.forms import EmailChangeForm
from apps.email_change.utils import generate_key
from apps.email_change.models import EmailChangeRequest
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib import messages

@login_required
def email_change_view(request, extra_context={},
        success_url='my-profile',#'email_verification_sent',
        template_name='email_change/email_change_form.html',
        email_message_template_name='email_change/emails/verification_email_message.html',
        email_subject_template_name='email_change/emails/verification_email_subject.html'):
    """Allow a user to change the email address associated with the user account.


    """
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email)

            if user and user != request.user:
                messages.error(request, "Podany adres jest już przypisany do innego użytkownika!")
                return render(request, template_name, {'form':form})

            verification_key = generate_key(request.user, email)

            current_site = Site.objects.get_current()
            site_name = current_site.name
            domain = current_site.domain

            protocol = 'http'
            if request.is_secure():
                protocol = 'https'

            # First clean all email change requests made by this user
            qs = EmailChangeRequest.objects.filter(user=request.user)
            qs.delete()

            # Create an email change request
            EmailChangeRequest.objects.create(
                user = request.user,
                verification_key = verification_key,
                email = email
                )

            # Prepare context
            c = {
                'email': email,
                'site_domain': domain,
                'site_name': site_name.replace('\n',''),
                'user': request.user,
                'verification_key': verification_key,
                'protocol': protocol,
            }
            c.update(extra_context)

            # Send success email
            subject = render_to_string(email_subject_template_name, c)
            message = render_to_string(email_message_template_name, c)
            
            send_mail('[Fereol] Weryfikacja zmiany adresu email', message, None, [email])
            messages.success(request, "Mail zawierający link weryfikacyjny został wysłany na Twój nowy adres email. Postępuj zgodnie z instrukcjami w tym mailu by z sukcesem zmienić Twój obecny adres email.")
            # Redirect
            return redirect(success_url)

    else:
        form = EmailChangeForm(instance=request.user)
    
    extra_context['form'] = form
    
    return render(request, template_name, extra_context)



@login_required
def email_verify_view(request, verification_key, extra_context={},
        success_url='my-profile',#'email_change_complete',
        template_name='email_change/email_verify.html'):
    try:
        ecr = EmailChangeRequest.objects.get(
            user=request.user, verification_key=verification_key)
    except EmailChangeRequest.DoesNotExist:
        # Return failure response
        return render(request, template_name, extra_context)
    else:
        # Check if the email change request has expired
        if ecr.has_expired():
            ecr.delete()
            # Return failure response
            return render(request, template_name, extra_context)
        
        # Success. Replace the user's email with the new email
        request.user.email = ecr.email
        request.user.save()
        messages.success(request, "Mail został pomyślnie zmieniony.")
        # Delete the email change request
        ecr.delete()

        # Redirect to success URL
        return redirect(success_url)

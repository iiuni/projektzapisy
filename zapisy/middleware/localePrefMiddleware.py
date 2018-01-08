# -*- coding: utf-8 -*-
from django.utils.translation import LANGUAGE_SESSION_KEY

from apps.users.models import UserProfile

class LocalePrefMiddleware(object):
    """This middleware checks if a user is authenticated, and if so, it sets
    locale settings accordingly to his preferences"""

    def process_request(self, request):
        if request.user.is_authenticated():
            if LANGUAGE_SESSION_KEY not in request.session:
                try:
                    account = UserProfile.objects.get(user=request.user)
                    request.session[LANGUAGE_SESSION_KEY] = account.preferred_language
                except UserProfile.DoesNotExist:
                    pass

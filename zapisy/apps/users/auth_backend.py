from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from apps.users.models import ExtendedUser

class ExtendedUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = ExtendedUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except ExtendedUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ExtendedUser.objects.get(pk=user_id)
        except ExtendedUser.DoesNotExist:
            return None


class BetterBackend(ModelBackend):

    def get_user(self, user_id):
        if hasattr(self, '__cached_user'):
            return self.__cached_user
        try:
            self.__cached_user = User.objects.select_related('profile', 'student', 'employee').get(pk=user_id)
            return self.__cached_user
        except User.DoesNotExist:
            return None
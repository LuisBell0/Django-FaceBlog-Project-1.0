from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    This authentication backend allows users to log in using either their username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by username
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            try:
                # If user is not found by username, try to fetch by email\
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                # Neither username nor email matched, return None
                return None

        if user.check_password(password):
            return user
        else:
            return None
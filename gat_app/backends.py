# gat_app/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # First, check if the input looks like a phone number (i.e., is all digits).
        if not username or not username.isdigit():
            # If it's not a number, this backend can't handle it.
            # Return None so Django tries the next backend (the default username one).
            return None

        # If it IS a number, proceed with the phone lookup.
        try:
            profile = UserProfile.objects.get(phone=username)
            user = profile.user
            if user.check_password(password):
                return user
        except UserProfile.DoesNotExist:
            return None


    def get_user(self, user_id):
        """
        Overrides the get_user method to retrieve a user by their ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
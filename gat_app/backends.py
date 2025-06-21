# gat_app/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile, LogBook

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the default authenticate method to allow login with a phone number.
        """
        try:
            # Find a user profile with the provided phone number.
            # The 'username' argument here is what the user enters in the form's main field.
            profile = UserProfile.objects.get(phone=username)

            # Get the actual User object associated with this profile.
            user = profile.user

            # Check if the provided password is correct for this user.
            if user.check_password(password):
                return user # Return the user object if authentication is successful.
            else:
                #User logon with incorrect password, save logbook
                LogBook.objects.create(
                    log_action='LOGIN: INCORRECT PWD',
                    log_result='FAILURE',
                    log_user_id=user.id,
                )
                return None
        except:
            # If no profile is found with that phone number, do nothing and let other backends try.
            return None

    def get_user(self, user_id):
        """
        Overrides the get_user method to retrieve a user by their ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
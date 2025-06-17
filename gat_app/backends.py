from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile, LogBook

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the default authenticate method to allow login with a phone number
        and logs login failures.
        """
        try:
            # 透過電話號碼尋找用戶設定檔
            profile = UserProfile.objects.get(phone=username)
            user = profile.user

            # 檢查密碼是否正確
            if user.check_password(password):
                # 密碼正確，認證成功
                return user
            else:
                # 用戶存在，但密碼錯誤
                LogBook.objects.create(
                    log_action='LOGIN',
                    log_result='FAILURE',
                    log_user=user,
                    log_details=f"Incorrect password for phone: {username}"
                )
                return None
        except UserProfile.DoesNotExist:
            # 找不到該電話號碼對應的用戶
            LogBook.objects.create(
                log_action='LOGIN',
                log_result='FAILURE',
                log_user=None, # 沒有對應的用戶
                log_details=f"User not found with phone: {username}"
            )
            return None

    def get_user(self, user_id):
        """
        Overrides the get_user method to retrieve a user by their ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
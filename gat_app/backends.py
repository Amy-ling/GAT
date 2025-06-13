# gat_app/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 檢查輸入的 username 是否為純數字
        if not username or not username.isdigit():
            # 如果不是數字，它不可能是電話號碼，此後端不處理，交給下一個後端（預設的 username 後端）
            return None

        # 如果是數字，則繼續用電話號碼來尋找使用者
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
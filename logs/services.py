from django.contrib.auth.models import User
from .models import LogBook

def create_log(user, action: str, result: str = 'success'):
    """
    一個方便建立 LogBook 紀錄的共用函式。
    現在 user 參數可以是一個 User 物件，也可以是 None。
    """
    # 由於模型已允許 log_user 為空，我們不再需要在這裡做 is_authenticated 檢查。
    # 即使傳入的是 AnonymousUser 或 None，我們也可以處理。

    log_user_instance = user
    if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
        # 如果傳入的不是一個已登入的使用者，就將實例設為 None
        log_user_instance = None

    LogBook.objects.create(
        log_user=log_user_instance,  # <-- 這裡現在可以接受 User 物件或 None
        log_action=action,
        log_result=result
    )
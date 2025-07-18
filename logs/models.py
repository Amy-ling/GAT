from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class LogBook(models.Model):
    log_action = models.CharField(max_length=20)
    log_result = models.CharField(max_length=10)
    log_date = models.DateTimeField(auto_now_add=True)
    log_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # 當 User 被刪除時，日誌的 user 欄位變為 NULL，而不是刪除日誌
        null=True,  # 允許資料庫中此欄位為空
        blank=True  # 允許在 Django Admin 或表單中此欄位為空
    )
    class Meta:
        db_table = 'gat_app_logbook'
    def __str__(self):
        return str(self.log_date)
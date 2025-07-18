from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'gat_app_userprofile'

    def __str__(self):
        return self.name
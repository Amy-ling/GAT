from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=50)
    phone = models.IntegerField(unique=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Item(models.Model):
    item_name = models.CharField(max_length=50)
    item_type = models.CharField(max_length=50)
    description = models.TextField(max_length=255, null=True, blank=True)
    give_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="give_user")
    give_date = models.DateTimeField(auto_now=True)
    item_state = models.CharField(max_length=20, default="available")

    def __str__(self):
        return self.item_name

class ItemTaken(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    take_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="take_user")
    take_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.item_id.item_name)

class ItemImage(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_image = models.ImageField(upload_to="item_image", null=True, blank=True)

    def __str__(self):
        return str(self.item_id.item_name)

class LogBook(models.Model):
    log_action = models.CharField(max_length=20)
    log_result = models.CharField(max_length=10)
    log_date = models.DateTimeField(auto_now_add=True)
    log_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="log_user", null=True, blank=True)
    log_details = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.log_date)

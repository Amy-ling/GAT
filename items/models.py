# items/models.py
from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    class ItemTypeChoices(models.TextChoices):
        ELECTRONICS = 'EL', 'Electronics'
        FURNITURE = 'FU', 'Furniture'
        BOOKS = 'BK', 'Books'
        CLOTHING = 'CL', 'Clothing'
        KITCHEN = 'KI', 'Kitchenware'
        TOYS = 'TY', 'Toys & Games'
        OTHER = 'OT', 'Other'

    item_name = models.CharField(max_length=50)
    item_type = models.CharField(
        max_length=2,
        choices=ItemTypeChoices.choices,
        default=ItemTypeChoices.OTHER
    )
    description = models.TextField(max_length=255, null=True, blank=True)
    give_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="give_user")
    give_date = models.DateTimeField(auto_now=True)
    item_state = models.CharField(max_length=20, default="available")

    class Meta:
        db_table = 'gat_app_item'

    def __str__(self):
        return self.item_name

class ItemTaken(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    take_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="take_user")
    take_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gat_app_itemtaken'
    def __str__(self):
        return str(self.item_id.item_name)

class ItemImage(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_image = models.ImageField(upload_to="item_image", null=True, blank=True)
    class Meta:
        db_table = 'gat_app_itemimage'

    def __str__(self):
        return str(self.item_id.item_name)
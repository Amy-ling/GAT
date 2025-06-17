from django.contrib import admin
from .models import UserProfile, Item, ItemImage, ItemTaken, LogBook

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(ItemTaken)
admin.site.register(LogBook)
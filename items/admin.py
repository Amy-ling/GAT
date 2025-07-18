from django.contrib import admin
from .models import Item, ItemImage, ItemTaken # 從本機的 models.py 導入

admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(ItemTaken)
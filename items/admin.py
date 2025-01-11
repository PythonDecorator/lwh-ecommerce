from django.contrib import admin

from .models import Category, Item


class ItemConfig(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_active', "timestamp"]
    search_fields = ['name', 'price', 'is_active', "timestamp"]
    filter = ['name', 'price', 'description']


admin.site.register(Item, ItemConfig)
admin.site.register(Category)

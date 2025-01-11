from django import forms

from items.models import Item, Category


class ItemCreateEditForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'image', 'is_active', 'price', 'discount_price', 'description']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image']

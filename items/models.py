from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.text import slugify


class ItemManager(models.Manager):

    def active_items(self):
        return self.filter(is_active=True)

    def in_active_items(self):
        return self.filter(is_active=False)

    def featured_items(self):
        return self.all().order_by('-view_count')


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='items')
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = ItemManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Name: {self.name} --Active: {self.is_active} --View-Count: {self.view_count}"

    @property
    def imageURL(self):
        try:
            if self.image:
                return self.image.url
        except:
            return None

    def get_absolute_url(self):
        return reverse("items:item_detail", kwargs={
            'slug': self.slug
        })

    def get_update_url(self):
        return reverse("items:item_update", kwargs={
            'id': self.id
        })

    def get_delete_url(self):
        return reverse("items:item_delete", kwargs={
            'pk': self.id
        })

    @property
    def review_count(self):
        return self.review_set.count()

    @property
    def reviews(self):
        return self.review_set.all()

    @property
    def real_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price


def create_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
    qs = Item.objects.filter(slug=slug).order_by('-id')
    if qs.exists():
        new_slug = f'{slug, qs.first().id}'
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Item)


class Category(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='category')

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            if self.image:
                return self.image.url
        except:
            return None

    @property
    def items_count(self):
        return self.item_set.count()

    def get_absolute_url(self):
        return reverse("items:category", kwargs={
            'id': self.id
        })


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    email = models.EmailField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

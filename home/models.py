from django.db import models

# Create your models here.
from django.utils import timezone

from items.models import Item


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=25)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=20000)
    timestamp = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']


class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=300)

    class Meta:
        ordering = ['-id']


class SubscribeEmail(models.Model):
    email = models.EmailField()

    class Meta:
        ordering = ['-id']

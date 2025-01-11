from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer',
        blank=True,
        null=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    device = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        try:
            return str(f"{self.user.email}--{self.first_name}--{self.last_name}")
        except:
            return str(f"{self.first_name} -- {self.last_name}")

    @property
    def imageURL(self):
        try:
            if self.image:
                return self.image.url
        except:
            return None

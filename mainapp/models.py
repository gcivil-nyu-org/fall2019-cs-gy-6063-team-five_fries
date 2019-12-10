from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from location.models import Location


class SiteUser(AbstractUser):
    full_name = models.CharField(max_length=255, default="")
    phone_number = PhoneNumberField(default="", blank=True, null=True)
    current_location = models.CharField(max_length=255, default="")
    work_location = models.CharField(max_length=255, default="")

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    favorites = models.ManyToManyField(Location, related_name="favorited_by")

    def __str__(self):
        return self.username

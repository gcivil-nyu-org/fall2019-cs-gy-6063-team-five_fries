from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class SiteUser(AbstractUser):
    full_name = models.CharField(max_length=255, default="")
    phone_number = PhoneNumberField(default="")
    current_location = models.CharField(max_length=255, default="")
    work_location = models.CharField(max_length=255, default="")

    user_type_string_map = {"T": "Tenant", "R": "Renter", "L": "Landlord"}
    user_type = models.CharField(
        max_length=2, choices=user_type_string_map.items(), default="R"
    )

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def user_type_string(self):
        return self.user_type_string_map.get(self.user_type, "")

    def __str__(self):
        return self.username

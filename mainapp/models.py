from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from enum import Enum


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_number = PhoneNumberField(default="")
    current_location = models.CharField(max_length=255, default="")
    work_location = models.CharField(max_length=255, default="")

    class UserType(Enum):
        TENANT = "T"
        RENTER = "R"
        LANDLORD = "L"

    user_type_string_map = {
        UserType.TENANT: "Tenant",
        UserType.RENTER: "Renter",
        UserType.LANDLORD: "Landlord",
    }

    user_type = models.CharField(
        max_length=2, choices=user_type_string_map.items(), default=UserType.RENTER
    )

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def user_type_string(self):
        user_type_enum = Profile.UserType(self.user_type)
        return Profile.user_type_string_map.get(user_type_enum, "")

    def __str__(self):
        return self.user.username


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

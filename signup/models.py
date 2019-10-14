from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class SignUp(models.Model):
    full_name = models.CharField(max_length=120, blank=False)
    user_name = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=20, blank=False)
    confirm_password = models.CharField(max_length=20, blank=False)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    current_location = models.CharField(max_length=255)
    work_location = models.CharField(max_length=255)

    TENANT = "T"
    RENTER = "R"
    LANDLORD = "L"
    USER_TYPE_CHOICES = [(TENANT, "Tenant"), (RENTER, "Renter"), (LANDLORD, "Landlord")]

    user_type = models.CharField(
        max_length=2, choices=USER_TYPE_CHOICES, default=RENTER
    )

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.user_name

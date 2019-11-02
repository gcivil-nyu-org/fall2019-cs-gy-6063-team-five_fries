from django.db import models
from localflavor.us import models as us_models


class Location(models.Model):
    city = models.CharField(max_length=100)
    state = us_models.USStateField()
    address = models.CharField(max_length=255)
    zipcode = us_models.USZipCodeField()
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
